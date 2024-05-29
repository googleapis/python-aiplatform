# -*- coding: utf-8 -*-
# Copyright 2019-2024 The TensorFlow Authors. All Rights Reserved.
# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Tests for tensorboard.uploader.logdir_loader."""

import logging
import os.path
import shutil
import tempfile

from google.cloud.aiplatform.tensorboard import logdir_loader
import tensorflow as tf

from tensorboard.backend.event_processing import directory_loader
from tensorboard.backend.event_processing import event_file_loader
from tensorboard.backend.event_processing import io_wrapper
from tensorboard.compat.proto import event_pb2
from tensorboard.compat.proto import graph_pb2
from tensorboard.compat.proto import meta_graph_pb2
from tensorboard.compat.proto import summary_pb2


class FileWriter(tf.compat.v1.summary.FileWriter):
    """FileWriter for test.

    TensorFlow FileWriter uses TensorFlow's Protobuf Python binding
    which is largely discouraged in TensorBoard. We do not want a
    TB.Writer but require one for testing in integrational style
    (writing out event files and use the real event readers).
    """

    def __init__(self, *args, **kwargs):
        # Briefly enter graph mode context so this testing FileWriter can be
        # created from an eager mode context without triggering a usage error.
        with tf.compat.v1.Graph().as_default():
            super(FileWriter, self).__init__(*args, **kwargs)

    def add_test_summary(self, tag, simple_value=1.0, step=None):
        """Convenience for writing a simple summary for a given tag."""
        value = summary_pb2.Summary.Value(tag=tag, simple_value=simple_value)
        summary = summary_pb2.Summary(value=[value])
        self.add_summary(summary, global_step=step)

    def add_test_tensor_summary(self, tag, tensor, step=None, value_metadata=None):
        """Convenience for writing a simple summary for a given tag."""
        value = summary_pb2.Summary.Value(
            tag=tag, tensor=tensor, metadata=value_metadata
        )
        summary = summary_pb2.Summary(value=[value])
        self.add_summary(summary, global_step=step)

    def add_event(self, event):
        if isinstance(event, event_pb2.Event):
            tf_event = tf.compat.v1.Event.FromString(event.SerializeToString())
        else:
            tf_event = event
            if not isinstance(event, bytes):
                logging.error(
                    "Added TensorFlow event proto. "
                    "Please prefer TensorBoard copy of the proto"
                )
        super(FileWriter, self).add_event(tf_event)

    def add_summary(self, summary, global_step=None):
        if isinstance(summary, summary_pb2.Summary):
            tf_summary = tf.compat.v1.Summary.FromString(summary.SerializeToString())
        else:
            tf_summary = summary
            if not isinstance(summary, bytes):
                logging.error(
                    "Added TensorFlow summary proto. "
                    "Please prefer TensorBoard copy of the proto"
                )
        super(FileWriter, self).add_summary(tf_summary, global_step)

    def add_session_log(self, session_log, global_step=None):
        if isinstance(session_log, event_pb2.SessionLog):
            tf_session_log = tf.compat.v1.SessionLog.FromString(
                session_log.SerializeToString()
            )
        else:
            tf_session_log = session_log
            if not isinstance(session_log, bytes):
                logging.error(
                    "Added TensorFlow session_log proto. "
                    "Please prefer TensorBoard copy of the proto"
                )
        super(FileWriter, self).add_session_log(tf_session_log, global_step)

    def add_graph(self, graph, global_step=None, graph_def=None):
        if isinstance(graph_def, graph_pb2.GraphDef):
            tf_graph_def = tf.compat.v1.GraphDef.FromString(
                graph_def.SerializeToString()
            )
        else:
            tf_graph_def = graph_def

        super(FileWriter, self).add_graph(
            graph, global_step=global_step, graph_def=tf_graph_def
        )

    def add_meta_graph(self, meta_graph_def, global_step=None):
        if isinstance(meta_graph_def, meta_graph_pb2.MetaGraphDef):
            tf_meta_graph_def = tf.compat.v1.MetaGraphDef.FromString(
                meta_graph_def.SerializeToString()
            )
        else:
            tf_meta_graph_def = meta_graph_def

        super(FileWriter, self).add_meta_graph(
            meta_graph_def=tf_meta_graph_def, global_step=global_step
        )


class LogdirLoaderTest(tf.test.TestCase):
    """Tests for LogdirLoader."""

    def get_temp_dir(self):
        if not hasattr(self, "_tempdir") or self._tempdir is None:
            self._tempdir = tempfile.mkdtemp()
        return self._tempdir

    def _create_logdir_loader(self, logdir):
        def directory_loader_factory(path):
            return directory_loader.DirectoryLoader(
                path,
                event_file_loader.TimestampedEventFileLoader,
                path_filter=io_wrapper.IsTensorFlowEventsFile,
            )

        return logdir_loader.LogdirLoader(logdir, directory_loader_factory)

    def _extract_tags(self, event_generator):
        """Converts a generator of tf.Events into a list of event tags."""
        return [
            event.summary.value[0].tag
            for event in event_generator
            if not event.file_version
        ]

    def _extract_run_to_tags(self, run_to_events):
        """Returns run-to-tags dict from run-to-event-generator dict."""
        run_to_tags = {}
        for run_name, event_generator in run_to_events.items():
            # There should be no duplicate runs.
            self.assertNotIn(run_name, run_to_tags)
            run_to_tags[run_name] = self._extract_tags(event_generator)
        return run_to_tags

    def test_empty_logdir(self):
        logdir = self.get_temp_dir()
        loader = self._create_logdir_loader(logdir)
        # Default state is empty.
        self.assertEmpty(list(loader.get_run_events()))
        loader.synchronize_runs()
        # Still empty, since there's no data.
        self.assertEmpty(list(loader.get_run_events()))

    def test_single_event_logdir(self):
        logdir = self.get_temp_dir()
        with FileWriter(logdir) as writer:
            writer.add_test_summary("foo")
        loader = self._create_logdir_loader(logdir)
        loader.synchronize_runs()
        self.assertEqual(
            self._extract_run_to_tags(loader.get_run_events()), {".": ["foo"]}
        )
        # A second load should indicate no new data for the run.
        self.assertEqual(self._extract_run_to_tags(loader.get_run_events()), {".": []})

    def test_multiple_writes_to_logdir(self):
        logdir = self.get_temp_dir()
        with FileWriter(os.path.join(logdir, "a")) as writer:
            writer.add_test_summary("tag_a")
        with FileWriter(os.path.join(logdir, "b")) as writer:
            writer.add_test_summary("tag_b")
        with FileWriter(os.path.join(logdir, "b", "x")) as writer:
            writer.add_test_summary("tag_b_x")
        with FileWriter(os.path.join(logdir, "b_z")) as writer:
            writer.add_test_summary("tag_b_z")
        writer_c = FileWriter(os.path.join(logdir, "c"))
        writer_c.add_test_summary("tag_c")
        writer_c.flush()
        loader = self._create_logdir_loader(logdir)
        loader.synchronize_runs()
        self.assertEqual(
            self._extract_run_to_tags(loader.get_run_events()),
            {
                "a": ["tag_a"],
                "b": ["tag_b"],
                "b-x": ["tag_b_x"],
                "b-z": ["tag_b_z"],
                "c": ["tag_c"],
            },
        )
        # A second load should indicate no new data.
        self.assertEqual(
            self._extract_run_to_tags(loader.get_run_events()),
            {"a": [], "b": [], "b-x": [], "b-z": [], "c": []},
        )
        # Write some new data to both new and pre-existing event files.
        with FileWriter(os.path.join(logdir, "a"), filename_suffix=".other") as writer:
            writer.add_test_summary("tag_a_2")
            writer.add_test_summary("tag_a_3")
            writer.add_test_summary("tag_a_4")
        with FileWriter(
            os.path.join(logdir, "b", "x"), filename_suffix=".other"
        ) as writer:
            writer.add_test_summary("tag_b_x_2")
        with writer_c as writer:
            writer.add_test_summary("tag_c_2")
        # New data should appear on the next load.
        self.assertEqual(
            self._extract_run_to_tags(loader.get_run_events()),
            {
                "a": ["tag_a_2", "tag_a_3", "tag_a_4"],
                "b": [],
                "b-x": ["tag_b_x_2"],
                "b-z": [],
                "c": ["tag_c_2"],
            },
        )

    def test_directory_deletion(self):
        logdir = self.get_temp_dir()
        with FileWriter(os.path.join(logdir, "a")) as writer:
            writer.add_test_summary("tag_a")
        with FileWriter(os.path.join(logdir, "b")) as writer:
            writer.add_test_summary("tag_b")
        with FileWriter(os.path.join(logdir, "c")) as writer:
            writer.add_test_summary("tag_c")
        loader = self._create_logdir_loader(logdir)
        loader.synchronize_runs()
        self.assertEqual(list(loader.get_run_events().keys()), ["a", "b", "c"])
        shutil.rmtree(os.path.join(logdir, "b"))
        loader.synchronize_runs()
        self.assertEqual(list(loader.get_run_events().keys()), ["a", "c"])
        shutil.rmtree(logdir)
        loader.synchronize_runs()
        self.assertEmpty(loader.get_run_events())

    def test_directory_deletion_during_event_loading(self):
        logdir = self.get_temp_dir()
        with FileWriter(logdir) as writer:
            writer.add_test_summary("foo")
        loader = self._create_logdir_loader(logdir)
        loader.synchronize_runs()
        self.assertEqual(
            self._extract_run_to_tags(loader.get_run_events()), {".": ["foo"]}
        )
        shutil.rmtree(logdir)
        runs_to_events = loader.get_run_events()
        self.assertEqual(list(runs_to_events.keys()), ["."])
        events = runs_to_events["."]
        self.assertEqual(self._extract_tags(events), [])


if __name__ == "__main__":
    tf.test.main()
