# Copyright 2017 StreamSets Inc.

"""Abstractions for interacting with StreamSets Data Collector."""

import logging
from datetime import datetime
from functools import wraps
from urllib.parse import urlparse
from uuid import uuid4

from . import sdc_api, sdc_models

logger = logging.getLogger(__name__)

# The `#:` constructs at the end of assignments are part of Sphinx's autodoc functionality.
DEFAULT_SDC_USERNAME = 'admin'  #:
DEFAULT_SDC_PASSWORD = 'admin'  #:
DEFAULT_START_STATUSES_TO_WAIT_FOR = ['RUNNING', 'FINISHED']  #:


class DataCollector:
    """Class to interact with StreamSets Data Collector.

    Either ``server_url`` OR ``sch_instance`` must be passed in.

    Args:
        server_url (:obj:`str`): URL of an existing SDC deployment with which to interact. If
            not set, the Test Framework will manage a Docker-based Data Collector instance.
        username (:obj:`str`, optional): SDC username. This is used when interacting with the SDC REST API,
            and the user must already exist. Default: :py:const:`streamsets.sdk.sdc.DEFAULT_SDC_USERNAME`
        password (:obj:`str`, optional): SDC password. Default: :py:const:`streamsets.sdk.sdc.DEFAULT_SDC_PASSWORD`
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`, optional): A StreamSets Control Hub instance.
            Default: ``None``
        dump_log_on_error (:obj:`bool`): Whether to output Data Collector logs when exceptions
            are raised by certain methods. Default: ``False``
    """
    def __init__(self,
                 server_url,
                 username=None,
                 password=None,
                 control_hub=None,
                 dump_log_on_error=False,
                 **kwargs):
        self.server_url = server_url
        self.username = username or DEFAULT_SDC_USERNAME
        self.password = password or DEFAULT_SDC_PASSWORD
        self.control_hub = control_hub
        self.dump_log_on_error = dump_log_on_error

        if self.server_url:
            sch_headers = {
                'X-SS-User-Auth-Token': self.control_hub.api_client.session.headers['X-SS-User-Auth-Token']
            } if self.control_hub else {}
            self.api_client = sdc_api.ApiClient(server_url=self.server_url,
                                                username=self.username,
                                                password=self.password,
                                                headers=sch_headers,
                                                dump_log_on_error=self.dump_log_on_error,
                                                **kwargs)

            # Keep track of the server_host so that tests that may need it (e.g. to set configurations) can use it.
            self.server_host = urlparse(self.server_url).netloc.split(':')[0]
        else:
            self.server_host = None

        # SDC stage definitions should be an attribute of this class, but we use a property for
        # access to handle necessary setup and synchronization tasks, so indicate internal use for
        # the underlying attribute with a leading underscore.
        self._stage_definitions = None

        self.pipelines = {}

    def dump_sdc_log_on_error(*dec_args, **dec_kwargs):
        """A Python Decorator to log SDC when errors happen.
        Args:
            *dec_args (:obj:, optional): Optional non key-worded arguments to be passed.
            **dec_kwargs (:obj:, optional): Optional key-worded arguments to be passed, such as `all`. `all` will
                log complete SDC.
        """
        def outer_func(func):
            @wraps(func)
            def wrapped(self, *args, **kwargs):
                log_time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')
                try:
                    return func(self, *args, **kwargs)
                except:
                    if self.dump_log_on_error:
                        sdc_log = (self.get_logs()
                                   if dec_kwargs.get('all') else self.get_logs().after_time(log_time_now))
                        if sdc_log:
                            logger.error('Error during `%s` call. SDC log follows ...', func.__name__)
                            print('------------------------- SDC log - Begins -----------------------')
                            print(sdc_log)
                            print('------------------------- SDC log - Ends -------------------------')
                    raise
            return wrapped

        if len(dec_args) == 1 and not dec_kwargs and callable(dec_args[0]):  # called without args
            return outer_func(dec_args[0])
        else:
            return outer_func

    @dump_sdc_log_on_error
    def add_pipeline(self, *pipelines):
        """Add one or more pipelines to the DataCollector instance.

        Args:
            *pipelines: One or more instances of :py:class:`streamsets.Pipeline`
        """
        for pipeline in set(pipelines):
            self.pipelines[pipeline.id] = pipeline

            # Only do the REST call to add the pipeline if an API client is available.
            if self.api_client:
                logger.info('Importing pipeline %s...', pipeline.id)
                response = self.api_client.import_pipeline(pipeline_id=pipeline.id,
                                                           pipeline_json=pipeline._data)
                try:
                    pipeline.id = response['pipelineConfig']['pipelineId']
                except KeyError:
                    pipeline.id = response['pipelineConfig']['info']['name']

                status_command = self.api_client.get_pipeline_status(pipeline_id=pipeline.id)
                status_command.wait_for_status(status='EDITED')

    @dump_sdc_log_on_error
    def remove_pipeline(self, *pipelines):
        """Remove one or more pipelines from the DataCollector instance.

        Args:
            *pipelines: One or more instances of :py:class:`streamsets.Pipeline`
        """
        for pipeline in set(pipelines):
            if self.api_client:
                logger.info('Deleting pipeline %s...', pipeline.id)
                self.api_client.delete_pipeline(pipeline_id=pipeline.id)
            del self.pipelines[pipeline.id]

    def get_pipeline_builder(self):
        """Get a PipelineBuilder instance with which a Pipeline can be created.

        Returns:
            An instance of :py:class:`streamsets.PipelineBuilder`
        """
        if not self.api_client:
            raise Exception('SDC must be started to get a PipelineBuilder instance.')

        # A PipelineBuilder instance takes an empty pipeline and a list of stage definitions as
        # arguments. To get the former, we generate a pipeline in SDC, export it, and then delete
        # it. For the latter, we simply pass along `self.stage_definitions`.
        create_pipeline_command = self.api_client.create_pipeline(pipeline_title='Pipeline Builder',
                                                                  auto_generate_pipeline_id=True)
        try:
            pipeline_id = create_pipeline_command.response.json()['info']['pipelineId']
        except KeyError:
            pipeline_id = create_pipeline_command.response.json()['info']['name']

        pipeline = self.api_client.export_pipeline(pipeline_id)
        self.api_client.delete_pipeline(pipeline_id)

        return sdc_models.PipelineBuilder(pipeline=pipeline,
                                          stage_definitions=self.stage_definitions)

    def enable_sch(self, sch):
        """Enables SCH integration with SDC. Note that authentication tokens must be set up in
        SDC as described in our documentation.

        Args:
            An instance of :py:class:`streamsets.ControlHub`
        """
        logger.info('Enabling SCH ...')
        self.sch = sch.api_client

    @dump_sdc_log_on_error
    def set_user(self, username, password=None):
        """
        Set the user with which to interact with SDC.

        Args:
            username (:obj:`str`): Username of user.
            password (:obj:`str`, optional): Password for user. Default: same as ``username``
        """
        self.username = username
        # If password isn't set, assume it's the same as the username to follow existing
        # conventions.
        self.password = password or username

        if self.api_client:
            self.api_client.set_user(self.username, self.password)

    @property
    def stage_definitions(self):
        """Get an SDC instance's stage definitions.

        Will return a cached instance of the stage definitions if called more than once.
        """
        if self._stage_definitions:
            return self._stage_definitions

        # Getting stage definitions from SDC requires a running deployment.
        if not self.api_client:
            raise Exception('SDC must be started to get stage definitions.')

        self._stage_definitions = self.api_client.get_definitions()['stages']
        return self._stage_definitions

    @dump_sdc_log_on_error
    def start_pipeline(self, pipeline, runtime_parameters=None, **kwargs):
        """Start a pipeline.

        Args:
            pipeline (:py:class:`streamsets.Pipeline`): The Pipeline instance.
            runtime_parameters (:obj:`dict`, optional): Collection of runtime parameters. Default: ``None``
            wait (:obj:`bool`, optional): Flag to enable `wait_for_statuses`. Default: ``True``
            wait_for_statuses (:obj:`str` or :obj:`list`, optional): Pipeline status(es) to wait on.
                Default: ``['RUNNING', 'FINISHED']``

        Returns:
            An instance of :py:class:`streamsets.sdc_api.PipelineCommand`
        """
        logger.info('Starting pipeline %s...', pipeline.id)
        pipeline_command = self.api_client.start_pipeline(pipeline_id=pipeline.id,
                                                          runtime_parameters=runtime_parameters)
        if kwargs.get('wait', True):
            pipeline_command.wait_for_status(status=kwargs.get('wait_for_statuses', DEFAULT_START_STATUSES_TO_WAIT_FOR))

        return pipeline_command

    @dump_sdc_log_on_error
    def stop_pipeline(self, pipeline, **kwargs):
        """Stop a pipeline.

        Args:
            pipeline (:py:class:`streamsets.Pipeline`): The pipeline instance.
            force (:obj:`bool`, optional): Force pipeline to stop. Default: ``False``
            wait (:obj:`bool`, optional): Flag to wait for pipeline to stop. Default: ``True``

        Returns:
            An instance of :py:class:`streamsets.sdc_api.StopPipelineCommand`
        """
        logger.info('Stopping pipeline %s...', pipeline.id)
        stop_command = self.api_client.stop_pipeline(pipeline_id=pipeline.id)

        if kwargs.get('force', False):
            # Note: Pipeline force stop is applicable only after a pipeline stop.
            stop_command = self.api_client.force_stop_pipeline(pipeline_id=pipeline.id)

        if kwargs.get('wait', True):
            stop_command.wait_for_stopped()

        return stop_command

    @dump_sdc_log_on_error
    def run_pipeline_preview(self, pipeline, rev=0, batches=1, batch_size=10, skip_targets=True, end_stage=None,
                             timeout=2000, stage_outputs_to_override_json=None, **kwargs):
        """Run pipeline preview.

        Args:
            pipeline (:obj:`streamsets.Pipeline`): The pipeline object.
            rev (:obj:`int`, optional): Pipeline revision. Default: ``0``
            batches (:obj:`int`, optional): Number of batches. Default: ``1``
            batch_size (:obj:`int`, optional): Batch size. Default: ``10``
            skip_targets (:obj:`bool`, optional): Skip targets. Default: ``True``
            end_stage (:obj:`str`, optional): End stage. Default: ``None``
            timeout (:obj:`int`, optional): Timeout. Default: ``2000``
            stage_outputs_to_override_json (:obj:`str`, optional): Stage outputs to override. Default: ``None``
            wait (:obj:`bool`, optional): Flag to wait for pipeline preview to finish. Default: ``True``

        Returns:
            An instance of `streamsets.sdc_api.PreviewCommand`
        """
        logger.info('Running preview for %s...', pipeline.id)
        preview_command = self.api_client.run_pipeline_preview(pipeline.id, rev, batches,
                                                               batch_size, skip_targets, end_stage,
                                                               timeout, stage_outputs_to_override_json)
        if kwargs.get('wait', True):
            preview_command.wait_for_finished()

        return preview_command

    @dump_sdc_log_on_error
    def get_snapshots(self, pipeline=None):
        """Get information about stored snapshots.

        Args:
            pipeline (:py:class:`streamsets.Pipeline`, optional): The pipeline instance. Default: ``None``

        Returns:
            A list of :py:class:`streamsets.sdc_models.SnapshotInfo` instances
        """
        snapshots = [sdc_models.SnapshotInfo(info) for info in self.api_client.get_snapshots()]
        return snapshots if not pipeline else [info for info in snapshots if info['name'] == pipeline.id]

    @dump_sdc_log_on_error
    def capture_snapshot(self, pipeline, snapshot_name=None, start_pipeline=False,
                         runtime_parameters=None, batches=1, batch_size=10, **kwargs):
        """Capture a snapshot for given pipeline.

        Args:
            pipeline (:obj:`streamsets.sdc_models.Pipeline`): The pipeline instance.
            snapshot_name (:obj:`str`, optional): Name for the generated snapshot. If set to ``None``,
                an auto-generated UUID (which can be recovered from the returned ``SnapshotCommand``
                object's ``snapshot_name`` attribute) will be used when calling the REST API. Default: ``None``
            start_pipeline (:obj:`bool`, optional): If set to true, then the pipeline will be
                started and its first batch will be captured. Otherwise, the pipeline must be
                running, in which case one of the next batches will be captured. Default: False
            runtime_parameters (:obj:`dict`, optional): Runtime parameters to override Pipeline Parameters value.
                Default: ``None``
            wait (:obj:`bool`, optional): Flag to enable capture snapshot to finish. Default: ``True``
            wait_for_statuses (:obj:`str` or :obj:`list`, optional): Pipeline start status(s) to wait on.
                Default: ``['RUNNING', 'FINISHED']``

        Returns:
            An instance of :py:class:`streamsets.sdc_api.SnapshotCommand`
        """
        logger.info('Capturing snapshot (%d batches of size %d) for %s...', batches, batch_size,
                    pipeline.id)
        snapshot_command = self.api_client.capture_snapshot(pipeline_id=pipeline.id,
                                                            snapshot_name=snapshot_name or str(uuid4()),
                                                            start_pipeline=start_pipeline,
                                                            runtime_parameters=runtime_parameters,
                                                            batches=batches, batch_size=batch_size)
        if start_pipeline:
            status_command = self.api_client.get_pipeline_status(pipeline_id=pipeline.id)
            status_command.wait_for_status(status=kwargs.get('wait_for_statuses',
                                                             DEFAULT_START_STATUSES_TO_WAIT_FOR))

        if kwargs.get('wait', True):
            snapshot_command.wait_for_finished()

        return snapshot_command

    @dump_sdc_log_on_error
    def get_pipeline_acl(self, pipeline):
        """Get pipeline ACL.

        Args:
            pipeline (:py:class:`streamsets.Pipeline`): The pipeline instance.

        Returns:
            An instance of :py:class:`streamsets.sdc_models.PipelineAcl`
        """
        return sdc_models.PipelineAcl(self.api_client.get_pipeline_acl(pipeline_id=pipeline.id))

    @dump_sdc_log_on_error
    def set_pipeline_acl(self, pipeline, pipeline_acl):
        """Update pipeline ACL.

        Args:
            pipeline (:py:class:`streamsets.Pipeline`): The pipeline instance.
            pipeline_acl (:py:class:`streamsets.sdc_models.PipelineAcl`): The pipeline ACL instance.

        Returns:
            An instance of :py:class:`streamsets.sdc_api.Command`
        """
        return self.api_client.set_pipeline_acl(pipeline_id=pipeline.id, pipeline_acl_json=pipeline_acl._data)

    @dump_sdc_log_on_error
    def get_pipeline_permissions(self, pipeline):
        """Return pipeline permissions for a given pipeline.

        Args:
            pipeline (:obj:`streamsets.Pipeline`): The pipeline instance.

        Returns:
            An instance of :py:class:`streamsets.sdc_models.PipelinePermissions`
        """
        return sdc_models.PipelinePermissions(self.api_client.get_pipeline_permissions(pipeline_id=pipeline.id))

    @dump_sdc_log_on_error
    def get_pipeline_status(self, pipeline):
        """Get status of a pipeline.

        Args:
            pipeline (:py:class:`streamsets.Pipeline`): The Pipeline instance.
        """
        logger.info('Getting status of pipeline %s...', pipeline.id)
        return self.api_client.get_pipeline_status(pipeline_id=pipeline.id)

    @dump_sdc_log_on_error
    def get_pipeline_history(self, pipeline):
        """
        Get a pipeline's history.

        Args:
            pipeline (:py:class:`streamsets.Pipeline`): The pipeline instance.

        Returns:
            An instance of :py:class:`streamsets.History`
        """
        logger.info('Getting pipeline history for %s...', pipeline.id)
        return sdc_models.History(self.api_client.get_pipeline_history(pipeline_id=pipeline.id))

    @property
    def current_user(self):
        """
        Get currently logged-in user and its groups and roles.

        Returns:
            An instance of :py:class:`streamsets.sdc_models.User`
        """
        logger.info('Getting current user ...')
        return sdc_models.User(self.api_client.get_current_user())

    def get_logs(self, ending_offset=-1, extra_message=None, pipeline=None, severity=None):
        """Get logs.

        Args:
            ending_offset (:obj:`int`): ending_offset.
            extra_message (:obj:`str`): extra_message.
            pipeline (:py:class:`streamsets.Pipeline`): The pipeline instance.
            severity (:obj:`str`): severity.

        Returns:
            An instance of :py:class:`streamsets.sdc_models.Log`
        """
        return sdc_models.Log(self.api_client.get_logs(ending_offset, extra_message,
                                                       pipeline, severity))

    def get_alerts(self):
        """Get pipeline alerts."""
        return sdc_models.Alerts(self.api_client.get_alerts())

    @dump_sdc_log_on_error
    def get_bundle_generators(self):
        """Get available support bundle generators."""
        return sdc_models.BundleGenerators(self.api_client.get_bundle_generators())

    @dump_sdc_log_on_error
    def get_bundle(self, generators=None):
        """Generate new Support bundle."""
        return self.api_client.get_bundle(generators)
