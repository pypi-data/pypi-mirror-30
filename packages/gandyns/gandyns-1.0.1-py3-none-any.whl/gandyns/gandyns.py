import argparse
import json
import logging
import re
import sys

import requests

IP_PROVIDER = 'http://ip.42.pl/raw'
GANDI_API = 'https://dns.api.gandi.net/api/v5'
DEFAULT_TTL = 300
LOG_FORMAT = "[%(asctime)s - %(name)s - %(levelname)s] %(message)s"


logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class GandiAPI:
    def __init__(self, url, key):
        self.url = url
        self.headers = {
          'Content-Type': 'application/json',
          'X-Api-Key': key
        }

    def get_record_value(self, zone_uuid, record_name, record_type):
        url = f'{self.url}/zones/{zone_uuid}/records/{record_name}/{record_type}'
        r = requests.get(url, headers=self.headers)
        record = r.json()

        return record['rrset_values'][0] if 'rrset_values' in record else None

    def update_record(self, zone_uuid, record_name, record_type, value):
        data = {
            'rrset_values': [value],
            'rrset_ttl': DEFAULT_TTL
        }
        url = f'{self.url}/zones/{zone_uuid}/records/{record_name}/{record_type}'
        return requests.put(url, headers=self.headers, data=json.dumps(data))


def get_public_ip():
    r = requests.get(IP_PROVIDER)
    ip = r.text
    return ip if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip) else None


def main():
    parser = argparse.ArgumentParser(
        description='Update gandi DNS record with current public IP'
    )
    parser.add_argument('api_key', type=str, help="gandi API key")
    parser.add_argument('zone_uuid', type=str, help="DNS zone uuid")
    parser.add_argument('record_name', type=str, help="DNS record name")
    parser.add_argument('record_type', type=str, help="DNS record type")

    args = parser.parse_args()

    logger.info('Update gandi DNS record')

    public_ip = get_public_ip()
    if public_ip:
        logger.info(f'Retrieved public ip: {public_ip}')
    else:
        logger.critical('Failed to retrieve a valid public ip address')
        sys.exit(1)

    api = GandiAPI(GANDI_API, args.api_key)

    current_value = api.get_record_value(args.zone_uuid, args.record_name, args.record_type)
    if current_value:
        logger.info(f'Retrieved current record value: {current_value}')
    else:
        logger.error('Failed to retrieve current record value')

    if current_value == public_ip:
        logger.info('Current record value matches the public ip. No need to update it.')
        sys.exit(0)

    result = api.update_record(args.zone_uuid, args.record_name, args.record_type, public_ip)
    if result.status_code == requests.codes.created:
        logger.info('Successfully updated the record')
    else:
        logger.critical(f'Failed to update the record. Status code: {result.status_code}. Answer: {result.text}')
        sys.exit(1)


if __name__ == "__main__":
    main()
