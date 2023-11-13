# Initialize an empty dictionary
import yaml

application_dict = {}
application_dict['config1'] = {}
application_dict['config1']['dap'] = {}
application_dict['config1']['dap']['dap1'] = {'Config1': 'Config1', 'Config2': 'Config2'}

# application_dict['genesys'] = {}
application_dict['config2'] = {'Config1': 'Config1', 'Config2': 'Config2'}

application_dict['config3'] = {}
application_dict['config3']['cfg'] = {}
application_dict['config3']['cfg']['fa10001'] = {'Config1': 'Config1', 'Config2': 'Config2'}
application_dict['config3']['cfg']['fa20002'] = {'Config1': 'Config1', 'Config2': 'Config2'}
application_dict['config3']['cfg']['fa30003'] = {'Config1': 'Config1', 'Config2': 'Config2'}

yaml_data = yaml.dump(application_dict, default_flow_style=False)

with open('application.yaml', 'w') as file:
    file.write(yaml_data)
