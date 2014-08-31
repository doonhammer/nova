#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import uuid

import mock

from nova import exception
from nova import objects
from nova.tests.objects import test_objects
from nova.virt import hardware

fake_numa_topology = hardware.VirtNUMAInstanceTopology(
        cells=[hardware.VirtNUMATopologyCell(0, set([1, 2]), 512),
               hardware.VirtNUMATopologyCell(1, set([3, 4]), 512)])

fake_db_topology = {
    'created_at': None,
    'updated_at': None,
    'deleted_at': None,
    'deleted': 0,
    'id': 1,
    'instance_uuid': str(uuid.uuid4()),
    'numa_topology': fake_numa_topology.to_json()
    }


class _TestInstanceNUMATopology(object):
    def test_create(self):
        topo_obj = objects.InstanceNUMATopology.obj_from_topology(
               fake_numa_topology)
        topo_obj.create(self.context, fake_db_topology['instance_uuid'])
        got = objects.InstanceNUMATopology.get_by_instance_uuid(
                self.context, fake_db_topology['instance_uuid'])
        self.assertIsNotNone(got)
        self.assertEqual(topo_obj.id, got.id)

    @mock.patch('nova.db.instance_extra_get_by_instance_uuid')
    def test_get_by_instance_uuid(self, mock_get):
        mock_get.return_value = fake_db_topology
        numa_topology = objects.InstanceNUMATopology.get_by_instance_uuid(
            self.context, 'fake_uuid')
        self.assertEqual(fake_db_topology['instance_uuid'],
                         numa_topology.instance_uuid)
        for obj_cell, topo_cell in zip(
                numa_topology.cells, fake_numa_topology.cells):
            self.assertIsInstance(obj_cell, objects.InstanceNUMACell)
            self.assertEqual(topo_cell.cpuset, obj_cell.cpuset)
            self.assertEqual(topo_cell.memory, obj_cell.memory)

    @mock.patch('nova.db.instance_extra_get_by_instance_uuid')
    def test_get_by_instance_uuid_missing(self, mock_get):
        mock_get.return_value = None
        self.assertRaises(
            exception.NumaTopologyNotFound,
            objects.InstanceNUMATopology.get_by_instance_uuid,
            self.context, 'fake_uuid')


class TestInstanceNUMATopology(test_objects._LocalTest,
                               _TestInstanceNUMATopology):
    pass


class TestInstanceNUMATopologyRemote(test_objects._RemoteTest,
                                     _TestInstanceNUMATopology):
    pass