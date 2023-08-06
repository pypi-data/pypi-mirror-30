import os.path
import subprocess
import shlex

from cis_client.lib.cis_north import access_key_client


def aspera_upload(
        aaa_host, username, password,
        north_host, ingest_point, path, destination_path=None, **kwargs):
    """Aspera upload"""

    if destination_path is None:
        destination_path = os.path.basename(path)

    ingest_point_info, access_key = access_key_client.get_access_key(
        aaa_host, username, password, north_host, ingest_point, **kwargs)

    # ascp -P 33001 <local-path> <access-key>@udn-1-1-is_ingest.cdx-dev.dataingest.net:<path>
    aspera_template = ingest_point_info['gateway']['protocols']['aspera']['template']
    aspera_cmd = aspera_template.replace('<local-path>', path, 1).replace('<access-key>', access_key, 1)
    aspera_cmd = '{}:{}'.format(aspera_cmd.rsplit(':', 1)[0], destination_path.lstrip('/'))
    aspera_cmd_args = shlex.split(aspera_cmd)
    aspera_cmd_args_resume = [aspera_cmd_args[0], '-k2', '-l1G']
    aspera_cmd_args_resume.extend(aspera_cmd_args[1:])
    subprocess.call(aspera_cmd_args_resume)
