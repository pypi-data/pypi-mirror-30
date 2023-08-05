from clinodes.nodes import ArgNode

from gofri.lib.project_generator.module_generator import generate_module
from gofri.lib.project_generator.templates import build_entity_file, build_filter_file

data = {}

class ModuleGeneratorNode(ArgNode):
    def setup(self):
        self.expects_more = True
        self.enable_any = True

    def run(self, *args_remained):
        name = args_remained[0]
        inner_path = args_remained[1]
        generate_module(
            root_package_path=data["root"],
            module_package=inner_path,
            name=name
        )

class ControllerGeneratorNode(ArgNode):
    def setup(self):
        self.expects_more = False
        self.enable_any = True

    def run(self, *args_remained):
        name = args_remained[0]
        inner_path = "{}.back.controller".format(data["root_base"])
        generate_module(
            root_package_path=data["root"],
            module_package=inner_path,
            name=name
        )


class DtoGeneratorNode(ArgNode):
    def setup(self):
        self.expects_more = False
        self.enable_any = True

    def run(self, *args_remained):
        name = args_remained[0]
        inner_path = "{}.back.dto".format(data["root_base"])
        generate_module(
            root_package_path=data["root"],
            module_package=inner_path,
            name=name
        )


class ServiceGeneratorNode(ArgNode):
    def setup(self):
        self.expects_more = False
        self.enable_any = True

    def run(self, *args_remained):
        name = args_remained[0]
        inner_path = "{}.back.service".format(data["root_base"])
        generate_module(
            root_package_path=data["root"],
            module_package=inner_path,
            name=name
        )


class EntityGeneratorNode(ArgNode):
    def setup(self):
        self.expects_more = False
        self.enable_any = True

    def run(self, *args_remained):
        name = args_remained[0]
        cols = args_remained[1::]
        print(cols)
        inner_path = "{}.back.entity".format(data["root_base"])
        generate_module(
            root_package_path=data["root"],
            module_package=inner_path,
            name=name,
            template=build_entity_file(data["root"], name, cols)
        )


class FilterGeneratorNode(ArgNode):
    def setup(self):
        self.expects_more = False
        self.enable_any = True

    def run(self, *args_remained):
        name = args_remained[0]
        print(name)
        inner_path = "{}.back.filter".format(data["root_base"])
        generate_module(
            root_package_path=data["root"],
            module_package=inner_path,
            name=name,
            template=build_filter_file(data["root"], name)
        )


class GenerateNode(ArgNode):
    def setup(self):
        self.commands = {
            "module" : ModuleGeneratorNode,
            "controller": ControllerGeneratorNode,
            "dto": DtoGeneratorNode,
            "service": ServiceGeneratorNode,
            "entity": EntityGeneratorNode,
            "filter": FilterGeneratorNode
        }
        self.expects_more = True

class RootNode(ArgNode):
    def setup(self):
        self.commands = {
            "generate": GenerateNode,
        }
        self.expects_more = True