import os
import sys
import time
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_path + '/../')
import unittest
from decimal import Decimal
from carpalrouting.optimize import Routing
from carpalrouting.models import Driver, Location, Coordinates
from carpalrouting.grouping import DriverGrouping, LocationGrouping
from data import drivers, locations


class TestOptimizer(unittest.TestCase):   
    def test_optimization_with_predefined_data(self):
        
        schedules = DriverGrouping().group_drivers_by_time_slot(
            drivers=[Driver(id=item.get('id'),
                            time_slots=item.get('time_slots'),
                            capacity=item.get('capacity'),
                            speed=item.get('speed')) for item in drivers])

        data, _ = LocationGrouping().group_locations(locations, schedules, True)

        self.assertEqual(len(_), 0)

        inhouse = []
        for pickup_address, pickup_windows in data.items():
            for pickup_window, obj in pickup_windows.items():
                locs = obj.get('locations')
                driver_ids = obj.get('driver_ids')
                while locs and driver_ids:
                    driver = None 
                    for item in drivers:
                        if item.get('id') == driver_ids[0]:
                            driver = item
                            break

                    filtered_indices = []
                    for k, v in enumerate(locs):
                        if v.capacity <= driver.get('capacity'):
                            filtered_indices.append(k)
                            
                    indices = Routing(locations=[loc for loc in locs if loc.capacity <= driver.get('capacity')],
                                      num_vehicles=len(locs)).generate_routes(
                                          vehicle_capacity=driver.get('capacity'),
                                          speed=driver.get('speed'),
                                          service_time_unit=1800)

                    if len(indices) == 0:                       
                        break
                    else:
                        #remove driver from available driver list only if a route has been built
                        driver_id = driver_ids.pop(0)                            

                        routes = []
                        for item in indices[0]:
                            if ';' in locs[filtered_indices[item]].ref:
                                for sub_item in locs[filtered_indices[item]].ref.split(';'):
                                    itm_info = sub_item.split(',')
                                    routes.append(
                                        Location(coordinates = Coordinates(
                                                    locs[filtered_indices[item]].coordinates[0], 
                                                    locs[filtered_indices[item]].coordinates[1]),
                                                 address = locs[filtered_indices[item]].address,
                                                 delivery_window = locs[filtered_indices[item]].delivery_window,
                                                 capacity = float(itm_info[1]),
                                                 ref = itm_info[0]))
                            else:
                                routes.append(locs[filtered_indices[item]])
                            if filtered_indices[item] != 0:
                                locs[filtered_indices[item]] = None
                        inhouse.append({driver_id: routes})
                        locs = list(filter(lambda x: x is not None, locs))
                obj['locations'] = locs if len(locs) > 1 else []


        public = []
        for pickup_address, pickup_windows in data.items():
            for pickup_window, obj in pickup_windows.items():
                locs = obj.get('locations')
                if locs:
                    indices = Routing(
                                locations=locs,
                                num_vehicles=len(locs)).generate_routes(
                                                                    vehicle_capacity=30,
                                                                    speed=30,
                                                                    service_time_unit=1800)

                    if len(indices) == 0:                    
                        break
                    else:                                                
                        for idx_list in indices:
                            routes = []

                            for item in idx_list:
                                if ';' in locs[item].ref:
                                    for sub_item in locs[item].ref.split(';'):
                                        itm_info = sub_item.split(',')
                                        routes.append(
                                            Location(coordinates = Coordinates(locs[item].coordinates[0], 
                                                                               locs[item].coordinates[1]),
                                                     address = locs[item].address,
                                                     delivery_window = locs[item].delivery_window,
                                                     capacity = float(itm_info[1]),
                                                     ref = itm_info[0]))
                                else:
                                    routes.append(locs[item])

                                if item != 0:
                                    locs[item] = None
                            public.append(routes)
                        locs = list(filter(lambda x: x is not None, locs))
                        obj['locations'] = locs if len(locs) > 1 else []
        
        inhouse, public = Routing.merge_routes(inhouse_routes=inhouse,
                                               public_routes=public,
                                               drivers=drivers)
        

        self.assertEqual(len(inhouse), 5)
        self.assertEqual(len(public), 3)
