import os
import re
import ast
import json
import shutil
import copy

import yaml
import yamlordereddictloader
from yamlordereddictloader import OrderedDict


class Merger:
    """
    Provides an API to merge an OpenAPI spec that is split into multiple files. For example, if you have a reference
    to an external document like this:
    $ref: cars/wheel.yaml#wheel
    mechanic will merge the reference to that schema into the original file, and then save a copy.
    """
    root_dir = ""
    EXTERNAL_SCHEMA_REGEX = "['\"]\$ref['\"]:\s['\"](?:\w|/)*\.(?:json|yaml|yml)#[/\w]*['\"]"

    def __init__(self, oapi_file, output_file):
        self.oapi_file = oapi_file
        self.oapi_obj = self._deserialize_file()
        self.output_file = output_file

    def merge(self):
        """
        Currently only supports referencing items that will end up in the components/schemas location in the spec file.
        """
        self._merge_schemas()
        self._write_to_file()

    def _deserialize_file(self):
        """
        Deserializes a file from either json or yaml and converts it to a dictionary structure to operate on.
        :param oapi_file:
        :return: dictionary representation of the OpenAPI file
        """
        if self.oapi_file.endswith(".json"):
            with open(self.oapi_file) as f:
                oapi = json.load(f)
        elif self.oapi_file.endswith(".yaml") or self.oapi_file.endswith(".yml"):
            with open(self.oapi_file) as f:
                oapi = yaml.load(f)
        else:
            raise SyntaxError("File is not of correct format. Must be either json or yaml (and filename extension must "
                              "one of those too).")
        self.root_dir = os.path.dirname(os.path.realpath(self.oapi_file))
        return oapi

    def follow_reference_link(self, ref, remote_only=False):
        """
        Gets a referenced object. Note, references must be in relation to the main OpenAPI file, not in relation to the
        current file.
        :param ref: reference link, example: #/components/schemas/Pet or pet.json#/Pet
        :param remote_only: flag to indicate if the caller is only interested in external references.
        :return: dictionary representation of the referenced object or None is ref is not external and remote_only=True.
        """
        is_link_in_current_file = True if ref.startswith("#/") else False

        if is_link_in_current_file and remote_only:
            return None

        if is_link_in_current_file:
            section = ref.split("/")[-3]
            object_type = ref.split("/")[-2]
            resource_name = ref.split("/")[-1]
            return self.oapi_obj[section][object_type][resource_name], resource_name
        else:
            filename = ref.split("#/")[0]
            object_name = ref.split("#/")[1]
            data = None

            with open(self.root_dir + "/" + filename) as f:
                if filename.endswith(".json"):
                    data = json.load(f)
                elif filename.endswith(".yaml") or filename.endswith(".yml"):
                    data = yaml.load(f)
                else:
                    raise SyntaxError(
                        "File is not of correct format. Must be either json or yaml (and filename extension must "
                        "one of those too).")

            return data[object_name]

    def _write_to_file(self):
        """
        Write the merged data into the specified output file.
        """
        with open(self.output_file, "w") as f:
            if self.output_file.endswith(".json"):
                json_data = json.dumps(self.oapi_obj, indent=3)
                f.write(json_data)
            elif self.output_file.endswith(".yaml") or self.output_file.endswith(".yml"):
                yaml_data = yaml.dump(OrderedDict(self.oapi_obj),
                                      Dumper=yamlordereddictloader.Dumper,
                                      default_flow_style=False)
                f.write(yaml_data)
            else:
                raise SyntaxError("Specified output file is not of correct format. Must be either json or yaml.")

    def _merge_schemas(self):
        """
        Merges referenced items into the components/schemas section of the specification file.
        """

        # convert the master file oapi dictionary into a string
        oapi_str = str(self.oapi_obj)
        # find all patterns in the string that match an external reference.
        matches = re.findall(self.EXTERNAL_SCHEMA_REGEX, oapi_str)

        # as long as there are matches, continue to merge the schemas
        while len(matches) > 0:
            for match in matches:
                reference = match.split(":")[1].replace("'", "").strip(" ")
                resource_name = reference.split("/")[-1]
                obj = self.follow_reference_link(reference, remote_only=True)

                if obj:
                    oapi_str = oapi_str.replace(match, '"$ref": "#/components/schemas/' + resource_name + '"')
                    # convert string back to a dictionary
                    self.oapi_obj = ast.literal_eval(oapi_str)

                    # if the object doesn't exist yet in the components/schemas section, add it.
                    if not self.oapi_obj["components"]["schemas"].get(resource_name):
                        self.oapi_obj["components"]["schemas"][resource_name] = obj

                    # set the string object for the next iteration of the loops.
                    oapi_str = str(self.oapi_obj)
            # find new matches after current iteration of merging schemas. Some of the merged schemas may have external
            # references as well, which would required several iterations of the while loop.
            matches = re.findall(self.EXTERNAL_SCHEMA_REGEX, oapi_str)


class SpecMerger:
    @staticmethod
    def clean(obj, key=None):
        if key:
            if isinstance(obj, list):
                for item in obj:
                    SpecMerger.clean(item, key=key)
            elif isinstance(obj, dict):
                if obj.get(key):
                    obj.pop(key)
                for k, v in obj.items():
                    SpecMerger.clean(v, key=key)

    @staticmethod
    def clean_schema_properties(obj):
        """
        Removes properties that have x-mechanic-db.model_only = true
        """
        iter_dict = copy.deepcopy(obj)

        for schema_name, schema in iter_dict['components']['schemas'].items():
            for index, allof_item in enumerate(schema.get('allOf', [])):
                if not allof_item.get('$ref'):
                    for prop_name, prop in allof_item.get('properties', {}).items():
                        if prop.get('x-mechanic-db', {}).get('model_only'):
                            obj['components']['schemas'][schema_name]['allOf'][index]['properties'].pop(prop_name)

            for prop_name, prop in schema.get('properties', {}).items():
                if prop.get('x-mechanic-db', {}).get('model_only'):
                    obj['components']['schemas'][schema_name]['properties'].pop(prop_name)
