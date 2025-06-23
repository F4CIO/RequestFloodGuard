from typing import Any

import geoip2.database

if __package__:
    from . import handler_for_file_system
else:
    import handler_for_file_system

DB_FILE_NAME_FOR_DBIP_CITY_LITE = 'dbip-city-lite.mmdb'
DB_FILE_NAME_FOR_DBIP_ASN_LITE = 'dbip-asn-lite.mmdb'

class HandlerForGeoIp:
    @staticmethod
    def get_city_info(ip_address: object) -> str | dict[str, str | None | float | Any]:

        # Create a reader object
        db_file_path = handler_for_file_system.build_sattelite_file_path(DB_FILE_NAME_FOR_DBIP_CITY_LITE)
        with geoip2.database.Reader(db_file_path) as reader:
            try:
                # Get the city information for the given IP address
                response = reader.city(ip_address)

                # Extract relevant information
                ip_info = {
                    'Country': response.country.name,
                    'Region': response.subdivisions.most_specific.name,
                    'City': response.city.name,
                    'Latitude': response.location.latitude,
                    'Longitude': response.location.longitude
                }
                return ip_info
            except geoip2.errors.AddressNotFoundError:
                return f"IP address {ip_address} not found in the database."
            except Exception as e:
                return str(e)

    @staticmethod
    def get_asn_info(ip_address: object) -> str | dict[str, str | None | float | Any]:

        # Create a reader object
        db_file_path = handler_for_file_system.build_sattelite_file_path(DB_FILE_NAME_FOR_DBIP_ASN_LITE)
        with (geoip2.database.Reader(db_file_path) as reader):
            try:
                # Get the city information for the given IP address
                response = reader.asn(ip_address)

                # Extract relevant information
                ip_info = {
                    'autonomous_system_organization': response.autonomous_system_organization,
                    'autonomous_system_number': response.autonomous_system_number,
                    'network': response.network
                }
                return ip_info
            except geoip2.errors.AddressNotFoundError:
                return f"IP address {ip_address} not found in the database."
            except Exception as e:
                return str(e)


# Example usage
if __name__ == "__main__":
    ip_address = '89.216.118.103' #'8.8.8.8'  # Replace with the IP address you want to look up
    result = HandlerForGeoIp.get_city_info(ip_address)
    print(result)

    result = HandlerForGeoIp.get_asn_info(ip_address)
    print(result)

