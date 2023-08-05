import os

import arcpy

from envipyarc import GPToolbox
from envipyengine import Engine
import envipyengine.config

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "ENVI Management Tools"
        self.alias = "envi"

        # List of tool classes associated with this toolbox
        self.tools = [CreateENVIToolbox, ConfigureENVIEnvironment]


class CreateENVIToolbox(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Create ENVI Toolbox"
        self.description = "Creates a python toolbox containing a tool generated from an ENVI Task."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        taskNames = arcpy.Parameter(
            displayName="ENVI Task Name(s)",
            name="taskNames",
            datatype="GPValueTable",
            parameterType="required",
            direction="input")

        # Toolbox Name
        outputToolbox = arcpy.Parameter(
            displayName="Output Toolbox",
            name="outputToolbox",
            datatype="DEToolbox",
            parameterType="required",
            direction="output")

        taskNames.columns = ([["GPString", "Task"]])

        return [taskNames, outputToolbox]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        # Get toolbox path.
        toolbox_path = os.path.abspath(parameters[1].valueAsText)
        # Get toolbox directory.
        toolbox_dir = os.path.dirname(os.path.realpath(toolbox_path))
        # Check writability.
        if not os.access(toolbox_dir, os.W_OK):
            messages.addErrorMessage("Toolbox directory is not writable.")
            raise arcpy.ExecuteError

        toolbox = GPToolbox([Engine('ENVI', cwd=arcpy.env.scratchFolder).task(task[0]) for task in parameters[0].value])
        toolbox.create_toolbox(parameters[1].valueAsText)

        return


class ConfigureENVIEnvironment(object):
    def __init__(self):
        """Configure the ENVI Engine."""
        self.label = "Configure ENVI Environment"
        self.description = "Configure the ENVI Engine to work with the ENVI Toolboxes."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        enginePath = arcpy.Parameter(
            displayName="Engine Location",
            name="enginePath",
            datatype="DEFile",
            parameterType="Required",
            direction="input")

        compileMode = arcpy.Parameter(
            displayName="Run Engine in Compile Mode",
            name="compileMode",
            datatype="GPBoolean",
            parameterType="optional",
            direction="input")

        useCustomENVIPath = arcpy.Parameter(
            displayName='Set path to ENVI Custom Code location',
            name='useCustomENVIPath',
            datatype='GPBoolean',
            parameterType='optional',
            direction='input')

        engineENVIpath = arcpy.Parameter(
            displayName='ENVI Custom Code location',
            name='engineENVIpath',
            datatype='GPString',
            parameterType='Optional',
            direction='Input')

        return [enginePath, compileMode, useCustomENVIPath, engineENVIpath]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def get_config_string(self, value_name):
        """ Return config value or null string ('') if value_name does not exist """
        try:
            return_value = envipyengine.config.get(value_name)
        except Exception as e:
            return_value = ''
        return return_value

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        
        # Engine path
        if parameters[0].value is None:
            taskengine_exe = self.get_config_string('engine')
            parameters[0].value = taskengine_exe

        # Compile checkbox
        if parameters[1].value is None:
            engine_args = self.get_config_string('engine-args')
            if '--compile' in engine_args:
                parameters[1].value = True
            else:
                parameters[1].value = False

        # Custom library path checkbox
        if parameters[2].value is None:
            environment = envipyengine.config.get_environment()
            if 'ENVI_CUSTOM_CODE' in environment:
                parameters[2].value = True
                parameters[3].value = environment['ENVI_CUSTOM_CODE']
            else:
                parameters[2].value = False

        # Set anablement of library path text field based on checkbox setting
        if parameters[2].value:
            parameters[3].enabled = True
        else:
            parameters[3].enabled = False

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""

        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        if parameters[0].value is not None:
            envipyengine.config.set('engine', parameters[0].valueAsText)
            messages.AddMessage('Setting Engine Executable Path: ' + str(parameters[0].valueAsText))
        
        # Toggle "--compile" in the engine arguments
        if parameters[1].value is not None:
            engine_args = self.get_config_string('engine-args')
            compile_present = '--compile' in engine_args
            if parameters[1].value:
                if not compile_present:
                    messages.AddMessage('Turning "--compile" on')
                    envipyengine.config.set('engine-args', '--compile ' + engine_args)
            else:
                if compile_present:
                    messages.AddMessage('Turning "--compile" off')
                    envipyengine.config.set('engine-args', engine_args.replace('--compile', '').strip())

        # if the checkbox is checked and there is a ENVI Custom Code path value, update it
        # otherwise remove the custom library path
        if parameters[2].value and parameters[3].value is not None:
            messages.AddMessage('Setting ENVI Library Path: ' + parameters[3].valueAsText)
            envi_custom_code = parameters[3].valueAsText
            environ = {'ENVI_CUSTOM_CODE': envi_custom_code}
            envipyengine.config.set_environment(environ)
        else:
            environment = envipyengine.config.get_environment()
            if 'ENVI_CUSTOM_CODE' in environment:
                messages.AddMessage('Removing ENVI Custom Code Path...')
                envipyengine.config.remove_environment('ENVI_CUSTOM_CODE')

        return
