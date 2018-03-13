# v0.15 modifed03132019 バグ修正
# v0.14 modifed03131711 充電プラグへの接続を実装
# v0.13 modifed03131141 SOCに応じた充電速度変化を実装
# v0.12 modifed03122006 クレードル・充電プラグの充電機能を実装



# ## パッケージ


import numpy
import random
import copy
import sys
import datetime
import pandas
import numpy
import matplotlib.pyplot as plot

input_filename = "inputdata.xlsx"
battery_sheetname = "Battery"
motorcycle_sheetname = "Motorcycle"
station_sheetname = "Station"
setup_sheetname = "Setup"

# ## データモデル及び処理（環境、バッテリー、モーターサイクル、ステーション）

class Service:
    def __init__(self):
        "SERRIVCE"

    def construct(self, battery_number, motorcycle_number):
        return battery_list, motocycle_list, statin_list

    def read_input(self):
        input_file = pandas.ExcelFile(input_filename)
        battery_input_df = input_file.parse(battery_sheetname)
        motorcycle_input_df = input_file.parse(motorcycle_sheetname)

    def set_battery(self, station, battery_input_df):
        battery_list = []
        for index, row in battery_input_df.iterrows():
            battery = Battery(station, row['max_capacity'],row["cur_capacity"], row["charge_times"], row["replace_times"])
            battery_list.append(battery)
        return battery_list

    def set_motorcycles(self, battery_list, motorcycle_input_df):
        motorcycle_list = []
        for index, row in motorcycle_input_df.iterrows():
            initial_mount = next((battery for battery in battery_list if battery.mount_in.__class__.__name__ == "Station"),None)
            drive_distance_pertime=(row["drive_distance_1"], row["drive_distance_2"], row["drive_distance_3"], row["drive_distance_4"], row["drive_distance_5"], row["drive_distance_6"], row["drive_distance_7"], row["drive_distance_8"], row["drive_distance_9"], row["drive_distance_10"], row["drive_distance_11"], row["drive_distance_12"], row["drive_distance_13"], row["drive_distance_14"], row["drive_distance_15"], row["drive_distance_16"], row["drive_distance_17"], row["drive_distance_18"], row["drive_distance_19"], row["drive_distance_20"], row["drive_distance_21"], row["drive_distance_22"], row["drive_distance_23"], row["drive_distance_24"])
            motorcycle_list.append(Motorcycle(initial_mount, drive_distance_pertime, row["swap_capacity"]))
        return motorcycle_list

class Circumstance:

    def __init__(self, time, station_list, motorcycle_list, all_battery_list):
        self.time = time
        self.station_list = station_list
        self.motorcycle_list = motorcycle_list
        self.all_battery_list = all_battery_list

    def _has_swappable_battery(self):
        flag = 0
        if self.time + 1 < 24:
            self.time += 1
        else :
            self.time = 1
        for motorcycle in self.motorcycle_list:
            target_station = random.choice(self.station_list)
            # print("motorcycle.battery",motorcycle.battery.cur_capacity)
            # print("self.battery.__class__.__name__",motorcycle.battery.__class__.__name__)
            #("motorcycle._cant_swap(target_station)", motorcycle._cant_swap(target_station).__class__.__name__)
            if motorcycle._cant_swap(target_station):
                return 0
            motorcycle.swap(target_station)
        return 1

    def count_plugged_motorcycle(self):
        plugged_motorcycle_number = 0
        for motorcycle in self.motorcycle_list:
            if motorcycle.plugged_flag == 1:
                plugged_motorcycle_number += 1
        return plugged_motorcycle_number

    #def random_connect(self):
    def lowest_battery_connect(self):
        lowest_battery = 100
        for motorcycle in self.motorcycle_list:
            if lowest_battery >= motorcycle.battery.cur_capacity and motorcycle.battery.cur_capacity >= swapping_threshhold and motorcycle.plugged_flag == 0:
                lowest_battery = motorcycle.battery.cur_capacity
        while True:
            for motorcycle in self.motorcycle_list:
                if motorcycle.battery.cur_capacity == lowest_battery and motorcycle.plugged_flag == 0:
                    motorcycle.connect_to_plug()
                    break
            # print("接続")
            break

    def time_progress(self):

        #時刻を進める
        if self.time + 1 < 24:
            self.time += 1
        else :
            self.time = 1

        #車両の行動

        ##充電プラグ接続車両のうち、走行開始する車両の接続が解除される

        # print(plug_number,"台の充電プラグに対し",self.count_plugged_motorcycle(),"台が接続中")
        disconnect_number = 0
        for motorcycle in self.motorcycle_list:
            if motorcycle.drive_distance_pertime[self.time] > 0 and motorcycle.plugged_flag == 1:
                motorcycle.disconnect_from_plug()
                disconnect_number += 1
                # print("走行開始で接続解除")
            elif motorcycle.battery.cur_capacity == motorcycle.battery.max_capacity and motorcycle.plugged_flag == 1:
                motorcycle.disconnect_from_plug()
                disconnect_number += 1
                print("満充電で接続解除")
        # print(disconnect_number, "台が接続解除")

        ##この時間に走行を行わない車両が最大数まで充電プラグに接続される
        connect_search = 0
        while True :
            if self.count_plugged_motorcycle() >= plug_number or connect_search >= plug_number:
                break
            # print(counter,"単位時間時点の",connect_search,"回目の接続先")
            self.lowest_battery_connect()
            connect_search += 1

        ##充電プラグ接続車両が充電される
        for motorcycle in self.motorcycle_list:
            if motorcycle.plugged_flag == 1:
                motorcycle.battery.charged_in_vehicle()

        ##電気容量が少ない車両がバッテリー交換を行う
        for motorcycle in self.motorcycle_list:
            if  motorcycle.plugged_flag == 0:
                motorcycle.swap(random.choice(self.station_list)) 

        #バッテリーの行動

        for battery in self.all_battery_list:
        ##充電回数に応じてバッテリー最大容量の劣化が発生する
            battery.deteriorate() 
        ##バッテリーがステーションに設置されていれば充電される
            if battery.mount_in.__class__.__name__ == "Station":
                battery.charged_on_cradle()
        ##バッテリーがバイクに設置されていれば電力が消費される 
            elif battery.mount_in.__class__.__name__ == "Motorcycle":
                battery.consume(self.time) 
        ##一定以上最大充電容量が下がったバッテリーをリプレースする
            battery.replace() 

    def replaced_battery_number(self):
        total_replace = 0
        for battery in self.all_battery_list:
            total_replace += battery.replace_times
        return total_replace
    
    def charged_battery_number(self):
        charge_count = 0
        for battery in self.all_battery_list:
            charge_count += battery.charge_times
        return charge_count
            
    def total_cost_calculation(self):
        initial_cost = len(self.all_battery_list) * battery_cost
        return self.replace_cost_calculation
    
    def output_battery_cur_capacity(self):
        output = []
        for battery in self.all_battery_list :
            output.append(battery.cur_capacity)
        return output
    
    def output_battery_max_capacity(self):
        output = []
        for battery in self.all_battery_list:
            output.append(battery.max_capacity)
        return output
    
    def output_battery_status(self):
        output = []
        for battery in self.all_battery_list:
            output.append(battery.mount_in.__class__.__name__)
        return output

class Battery:
    def __init__(self, mount_in, max_capacity, cur_capacity, charge_times, replace_times):
        self.mount_in = mount_in
        self.max_capacity = max_capacity
        self.cur_capacity = cur_capacity
        self.charge_times = charge_times
        self.replace_times = replace_times

    def charged_on_cradle(self):
        if self.cur_capacity < 80 and self.cur_capacity + cradle_charge_speed_below80 <80:
            self.cur_capacity += cradle_charge_speed_below80
        elif self.cur_capacity < 80 and 80 < self.cur_capacity + cradle_charge_speed_below80 and self.cur_capacity + cradle_charge_speed_below80 < self.max_capacity:
            self. cur_capacity += cradle_charge_speed_above80 * (1 - (80 - self.cur_capacity)/cradle_charge_speed_below80)
        elif 80 < self.cur_capacity and self.cur_capacity + cradle_charge_speed_above80 <= self.max_capacity:
            self.cur_capacity += cradle_charge_speed_above80
        elif 80  < self.cur_capacity and self.max_capacity  < self.cur_capacity + cradle_charge_speed_above80:
            self.cur_capacity += self.max_capacity

    def charged_in_vehicle(self):
        if self.cur_capacity < 80 and self.cur_capacity + vehicle_charge_speed_below80 <80:
            self.cur_capacity += vehicle_charge_speed_below80
        elif self.cur_capacity < 80 and 80 < self.cur_capacity + vehicle_charge_speed_below80 and self.cur_capacity + vehicle_charge_speed_below80 < self.max_capacity:
            self. cur_capacity += vehicle_charge_speed_above80 * (1 - (80 - self.cur_capacity)/vehicle_charge_speed_below80)
        elif 80 < self.cur_capacity and self.cur_capacity + vehicle_charge_speed_above80 <= self.max_capacity:
            self.cur_capacity += vehicle_charge_speed_above80
        elif 80  < self.cur_capacity and self.max_capacity  < self.cur_capacity + vehicle_charge_speed_above80:
            self.cur_capacity += self.max_capacity

    def consume(self, time):
        self.cur_capacity = self.cur_capacity - (self.mount_in.drive_distance_pertime[time])/denpi/battery_kWh*100
        if self.cur_capacity < 0:
            self.cur_capacity =  0

    def deteriorate(self):
        self.max_capacity = 100 - (self.charge_times * battery_deteriorating_rate) 

    def replace(self):
        if self.max_capacity < replace_threshhold:
            self.replace_times += 1
            self.max_capacity = 100
            self.charge_times = 0

class Motorcycle:

    def __init__(self, battery, plugged_flag, drive_distance_pertime, swap_capacity):
        self.battery = battery
        self.swap_capacity = swap_capacity
        self.drive_distance_pertime = drive_distance_pertime
        self.plugged_flag = 0

    def connect_to_plug(self):
        self.plugged_flag = 1

    def disconnect_from_plug(self):
        self.plugged_flag = 0

    def swap(self, target_station):
        # print("self.cur_capacity",self.battery.cur_capacity)
        if self.battery.cur_capacity < self.swap_capacity:
            swap_flag=0
            # print("swap")
            for battery in target_station.mounted_batteries():
                if battery.cur_capacity > charge_threshhold:
                    self.battery.mount_in = target_station #ステーションにバッテリーを戻す
                    self.battery.charge_times += 1
                    self.battery = battery #代わりにステーションからバッテリーを取得する
                    self.battery.mount_in = self #バイクに取得したバッテリーを差し込む
                    swap_flag=1
                    break

            if swap_flag==0:
                print("充電済みバッテリーなし")
            #     # for motorcycle in motorcycle_list:
            #     #     print("all now charged :", battery.cur_capacity)
            #     # for battery in target_station.mounted_batteries():
            #     #     print("station now charged :", battery.cur_capacity)
            #     #sys.exit()

    def random_swap(self, target_station):
        candidate_battery_list = []
        if self.battery.cur_capacity < self.swap_capacity:
            swap_flag=0
            for battery in target_station.mounted_batteries():
                if battery.cur_capacity > charge_threshhold:
                    self.battery.mount_in = target_station #ステーションにバッテリーを戻す
                    self.battery.charge_times += 1 #バッテリーの充電回数が増える
                    self.battery = battery #代わりにステーションからバッテリーを取得する
                    self.battery.mount_in = self #バイクに取得したバッテリーを差し込む
                    swap_flag=1
                    break

            if swap_flag==0:
                print("充電済みバッテリーなし")
                for battery in all_battery_list:
                    print("now charged :", battery.cur_capacity)
                #sys.exit()

    def _cant_swap(self, target_station):
        if self.battery.cur_capacity < self.swap_capacity:
            for battery in target_station.mounted_batteries():
                if battery.cur_capacity > charge_threshhold:
                    return 0
            return 1

class Station:
    def __init__(self):
        self.station_name = "STATION"

    def mounted_batteries(self):
        mounted_battery_list = []
        for battery in all_battery_list:
            if battery.mount_in.__class__.__name__ == "Station" :
                mounted_battery_list.append(battery)
        return mounted_battery_list

# ## 最小バッテリー算出

minimum_battery_flag=0

if __name__ == '__main__':

    print("実行開始")

    output_cur_capacity = []

    #定数
    time= 0
    counter = 0
    battery_cost= 50
    cradle_charge_speed_below80 = 25.8
    cradle_charge_speed_above80 = 15.4
    vehicle_charge_speed_below80 = 16.0
    vehicle_charge_speed_above80 = 11.8
    simulation_total_time = 24 * 30
    battery_deteriorating_rate = 20/700
    denpi = 22.7
    battery_kWh  = 1.046
    charge_threshhold = 70
    swapping_threshhold = 20
    replace_threshhold = 80
    trial_time = 0
    plug_number = 10
    plugged_motorcycle_number = 0

    minimum_battery_flag = 0
    counter = 0

    service = Service()

    #Excel読み込み
    input_file = pandas.ExcelFile(input_filename)
    battery_input_df = input_file.parse(battery_sheetname)
    motorcycle_input_df = input_file.parse(motorcycle_sheetname)
    motorcycle_number = len(motorcycle_input_df.index)
    battery_number = len(battery_input_df.index)

    # print(motorcycle_input_df)
    # print("battery_input_df.column",len(battery_input_df.columns))

    #ステーション
    station_list = []
    station = Station()
    station_list.append(station)

#--------------------------------------------------------------------------------------------------
    # while minimum_battery_flag < 1:
    #     #初期セットアップ（バッテリー、バイク、ステーション）

    #     # #バッテリー
    #     all_battery_list = [Battery(station, 100, 100, 0, 0) for i in range(battery_number)]
    #     for i in range(trial_time):
    #         all_battery_list.pop()

    #     # all_battery_list = service.set_battery(station ,battery_input_df)
    #     motorcycle_list = []
    #     motorcycle_id = 0
    #     for index, row in motorcycle_input_df.iterrows():
    #         drive_distance_pertime=(row["drive_distance_1"], row["drive_distance_2"], row["drive_distance_3"], row["drive_distance_4"], row["drive_distance_5"], row["drive_distance_6"], row["drive_distance_7"], row["drive_distance_8"], row["drive_distance_9"], row["drive_distance_10"], row["drive_distance_11"], row["drive_distance_12"], row["drive_distance_13"], row["drive_distance_14"], row["drive_distance_15"], row["drive_distance_16"], row["drive_distance_17"], row["drive_distance_18"], row["drive_distance_19"], row["drive_distance_20"], row["drive_distance_21"], row["drive_distance_22"], row["drive_distance_23"], row["drive_distance_24"])
    #         motorcycle_list.append(Motorcycle(all_battery_list[motorcycle_id], drive_distance_pertime, row["swap_capacity"]))
    #         all_battery_list[motorcycle_id].mount_in = motorcycle_list[motorcycle_id]    
    #         motorcycle_id += 1

        
    #     # #車輛
    #     # motorcycle_list = []
    #     # swap_capacity = 30
    #     # for motorcycle in range(5):
    #     #     initial_mount = next((battery for battery in all_battery_list if battery.mount_in.__class__.__name__ == "Station"),None)
    #     #     motorcycle_list.append(Motorcycle(initial_mount, drive_distance_pertime_1, swap_capacity))
    #     #     initial_mount.mount_in = motorcycle_list[counter]
    #     #環境
        # circumstance = Circumstance(time, station_list, motorcycle_list, all_battery_list)

    #     print("motorcycle number", len(motorcycle_list))
    #     print("battery number", len(all_battery_list))

    #     #時間経過
    #     for i in range(simulation_total_time):
    #         if not circumstance._has_swappable_battery():
    #             minimum_battery_flag = 1
    #         circumstance.time_progress()
    #         # for i in motorcycle_list:
    #         #     # print("motorcycle.battery.cur_capacity", i.battery.cur_capacity)
    #         # counter += 1
        
    #     trial_time +=1
    #     print("try ",trial_time," times" )
    #     #print("minimum_battery_flag",minimum_battery_flag)
    
    # print("minimum battery # is",len(all_battery_list))
    # print("finish")


#--------------------------------------------------------------------------------------------------
    all_battery_list = [Battery(station, 100, 100, 0, 0) for i in range(battery_number)]

    #車輛

    motorcycle_list = []
    motorcycle_id = 0
    for index, row in motorcycle_input_df.iterrows():
        drive_distance_pertime=(row["drive_distance_1"], row["drive_distance_2"], row["drive_distance_3"], row["drive_distance_4"], row["drive_distance_5"], row["drive_distance_6"], row["drive_distance_7"], row["drive_distance_8"], row["drive_distance_9"], row["drive_distance_10"], row["drive_distance_11"], row["drive_distance_12"], row["drive_distance_13"], row["drive_distance_14"], row["drive_distance_15"], row["drive_distance_16"], row["drive_distance_17"], row["drive_distance_18"], row["drive_distance_19"], row["drive_distance_20"], row["drive_distance_21"], row["drive_distance_22"], row["drive_distance_23"], row["drive_distance_24"])
        motorcycle_list.append(Motorcycle(all_battery_list[motorcycle_id], 0, drive_distance_pertime, row["swap_capacity"]))
        all_battery_list[motorcycle_id].mount_in = motorcycle_list[motorcycle_id]    
        motorcycle_id += 1
    circumstance = Circumstance(time, station_list, motorcycle_list, all_battery_list)
    print("初期化完了")

    for i in range(simulation_total_time):
        circumstance.time_progress()
        counter += 1
        charged_time = 0

    #     # motorcycle_list = []
    #     # swap_capacity = 30
    #     # for motorcycle in range(5):
    #     #     initial_mount = next((battery for battery in all_battery_list if battery.mount_in.__class__.__name__ == "Station"),None)
    #     #     motorcycle_list.append(Motorcycle(initial_mount, drive_distance_pertime_1, swap_capacity))
    #     #     initial_mount.mount_in = motorcycle_list[counter]
        if counter%24 == 0:
            print(counter/24, "日経過")

        if counter%(365*24) == 0:
            print(counter/(365*24),"年経過時点で交換バッテリー",circumstance.replaced_battery_number(),"個")
            charged_time =0
            total_replace =0
            for battery in circumstance.all_battery_list:
                charged_time += battery.charge_times
            print ("total charge times is ", charged_time)
            for i in all_battery_list:
                total_replace += i.replace_times
            print("total replace",total_replace)


    print("finish")
#--------------------------------------------------------------------------------------------------
