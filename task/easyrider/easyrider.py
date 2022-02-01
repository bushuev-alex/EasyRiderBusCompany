import json
import re


class DataChecker:
    def __init__(self):
        self.stop_list = None
        self.stop_dic = {}
        self.stop_id_time = {}
        self.dic_stage_6 = {}
        self.validation_required = {"bus_id": 0,
                                    "stop_id": 0,
                                    "stop_name": 0,
                                    "next_stop": 0,
                                    "stop_type": 0,
                                    "a_time": 0}
        self.start_stops = []
        self.finish_stops = []
        self.transfer_stops = []

    def check_json(self):
        for stop in self.stop_list:
            if not (isinstance(stop['bus_id'], int) and
                    re.match("\d+", f"{stop['bus_id']}")):
                self.validation_required["bus_id"] += 1
            if not (isinstance(stop['stop_id'], int) and
                    re.match("\d+", f"{stop['stop_id']}")):
                self.validation_required["stop_id"] += 1
            if not (isinstance(stop['stop_name'], str) and
                    re.match(r"(([A-Z]\w+) )+(Avenue|Boulevard|Road|Street)$", stop['stop_name'])):
                self.validation_required["stop_name"] += 1
            if not (isinstance(stop['next_stop'], int) and
                    re.match("\d+", f"{stop['next_stop']}")):
                self.validation_required["next_stop"] += 1
            if not (isinstance(stop['stop_type'], str) and
                    re.match("^(|[SOF])$", f"{stop['stop_type']}")):
                self.validation_required["stop_type"] += 1
            if not (isinstance(stop['a_time'], str) and
                    re.match("(2[0-4]|[0-1][0-9]):([0-5][0-9])$", f"{stop['a_time']}")):
                self.validation_required["a_time"] += 1

    def check_bus_lines(self):
        stop_dict = {}
        for stop in self.stop_list:
            stop_ = {stop["bus_id"]: 1}
            try:
                stop_dict[stop["bus_id"]] += 1
            except KeyError:
                stop_dict.update(stop_)
        print("Line names and number of stops:")
        for k, v in stop_dict.items():
            print(f"bus_id: {k}, stops: {v}")

    def read_json(self):
        js_data = input()
        self.stop_list = json.loads(js_data)

    def validation_result(self):
        print(f"Format validation: {sum(self.validation_required.values())} errors")
        for k, v in self.validation_required.items():
            if k in ("stop_name", "stop_type", "a_time"):
                print(': '.join([k, str(v)]))

    def create_stop_dict(self, stop):
        if stop["stop_type"] == 'S':
            self.stop_dic[stop["bus_id"]]["stop_s"] += 1
            self.stop_dic[stop["bus_id"]]["s_name"].append(stop["stop_name"])
        elif stop["stop_type"] == 'F':
            self.stop_dic[stop["bus_id"]]["stop_f"] += 1
            self.stop_dic[stop["bus_id"]]["f_name"].append(stop["stop_name"])
        else:
            self.stop_dic[stop["bus_id"]]["stop_t"] += 1
            self.stop_dic[stop["bus_id"]]["t_name"].append(stop["stop_name"])

    def function_stage_4(self):
        for stop_ in self.stop_list:
            try:
                self.create_stop_dict(stop_)
            except KeyError:
                stop_by_id = {stop_["bus_id"]: {"stop_s": 0, "stop_f": 0, "stop_t": 0,
                                                "s_name": [], "f_name": [], "t_name": [],
                                                "time": []
                                                }
                              }
                self.stop_dic.update(stop_by_id)
                self.create_stop_dict(stop_)
        # stop_dict looks like
        # {128: {"stop_s": 2, "stop_f": 2, "stop_t": 3,
        #        "s_name": [], "f_name": [], "t_name": [], "time": [] },
        #  512: {"stop_s": 3, "stop_f": 4, "stop_t": 5,
        #        "s_name": [], "f_name": [], "t_name": [], "time": [] },
        #  }

        for stop in self.stop_dic:
            # print(self.stop_dic[stop])
            if self.stop_dic[stop]["stop_s"] != 1 or self.stop_dic[stop]["stop_f"] != 1:
                print(f"There is no start or end stop for the line: {stop}.")
                return False
            else:
                self.start_stops += self.stop_dic[stop]["s_name"]
                self.transfer_stops += self.stop_dic[stop]["t_name"]
                self.finish_stops += self.stop_dic[stop]["f_name"]
        return True

    def function_stage_4_2(self):
        self.transfer_stops = self.transfer_stops + self.start_stops + self.finish_stops
        self.transfer_stops = [x for x in self.transfer_stops if self.transfer_stops.count(x) > 1]
        print("Start stops:", len(list(set(self.start_stops))), sorted(list(set(self.start_stops))))
        print("Transfer stops:", len(list(set(self.transfer_stops))), sorted(set(list(self.transfer_stops))))
        print("Finish stops:", len(list(set(self.finish_stops))), sorted(list(set(self.finish_stops))))

    def function_stage_5(self):
        for stop in self.stop_list:
            try:
                self.stop_id_time[stop["bus_id"]]["id"].append(stop["stop_id"])
                self.stop_id_time[stop["bus_id"]]["time"].append(stop["a_time"])
                self.stop_id_time[stop["bus_id"]]["time_name"].append(stop["stop_name"])
            except KeyError:
                time_by_id = {stop["bus_id"]: {"id": [], "time": [], "time_name": []}}
                self.stop_id_time.update(time_by_id)
                self.stop_id_time[stop["bus_id"]]["id"].append(stop["stop_id"])
                self.stop_id_time[stop["bus_id"]]["time"].append(stop["a_time"])
                self.stop_id_time[stop["bus_id"]]["time_name"].append(stop["stop_name"])
        # stop_id_time looks like
        # {128: {'id': [1, 3, 5, 7], 'time': ['08:12', '08:19', '08:25', '08:37'], 'time_name': []},
        #  512: {'id': [4, 6], 'time': ['08:13', '08:16'], 'time_name': []}
        #  }

    def function_stage_5_2(self):
        n = 0
        # print("Arrival time test:")
        for stop_ in self.stop_id_time:
            previous_id_time = [0, '0']
            for id_, time, time_name in zip(self.stop_id_time[stop_]["id"], self.stop_id_time[stop_]["time"],
                                            self.stop_id_time[stop_]["time_name"]):
                if previous_id_time[1] < time:
                    previous_id_time[0] = id_
                    previous_id_time[1] = time
                else:
                    previous_id_time[0] = id_
                    previous_id_time[1] = time
                    print(f"bus_id line {stop_}: wrong time on station {time_name}")
                    n += 1
        if n == 0:
            return True
        else:
            return False

    def function_stage_6(self):
        for stop_ in self.stop_list:
            try:
                self.create_stop_dict(stop_)
            except KeyError:
                stop_by_id = {stop_["bus_id"]: {"stop_s": 0, "stop_f": 0, "stop_t": 0,
                                                "s_name": [], "f_name": [], "t_name": [],
                                                "time": []
                                                }
                              }
                self.stop_dic.update(stop_by_id)
                self.create_stop_dict(stop_)

        for stop in self.stop_dic:
            self.start_stops += self.stop_dic[stop]["s_name"]
            self.finish_stops += self.stop_dic[stop]["f_name"]

            self.transfer_stops += self.stop_dic[stop]["t_name"]
        self.transfer_stops = self.transfer_stops + self.start_stops + self.finish_stops
        self.transfer_stops = [x for x in self.transfer_stops if self.transfer_stops.count(x) > 1]

    def function_stage_6_2(self):
        n = 0
        wrong_stops = []
        for stop in self.stop_list:
            # print(set(self.start_stops + self.finish_stops + self.transfer_stops))
            if stop["stop_type"] == "O" and stop["stop_name"] in set(self.start_stops + self.finish_stops + self.transfer_stops):
                n += 1
                wrong_stops.append(stop["stop_name"])
        if n == 0:
            print("OK")
        else:
            print(f"Wrong stop type: {sorted(list(set(wrong_stops)))}")


my_checker = DataChecker()
my_checker.read_json()
# my_checker.check_json()
# my_checker.validation_result()
# my_checker.check_bus_lines()
# if my_checker.function_stage_4():
#     my_checker.function_stage_4_2()
# my_checker.function_stage_5()
# if my_checker.function_stage_5_2():
#     print("OK")
my_checker.function_stage_6()
my_checker.function_stage_6_2()
