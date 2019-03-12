#! python
# My Log Parser
import statistics
import time
from datetime import datetime, timedelta
from pathlib import Path
from operator import add, sub, truediv
from time import strptime

from utils import grp
from utils.grp import Grp
from utils.metric import Metric

datafolder = Path("files")
fname = datafolder / "thy_log_20000"
ofname = ""  # original


class M:
    young = ["[PSYoungGen:", "[ParNew:"]
    old = ["[CMS:", '[ParOldGen:']
    perm = ["Metaspace"]

    def __init__(self):
        self.young = M.young[0]
        self.old = M.old[0]
        self.perm = M.perm[0]


class Graphics:
    minor = Grp(13)
    """timestamp, time_elapsed, reason, yg_before, yg_after, yg_allocated,
    heap_before, heap_after, heap_allocated, duration, times_user, times_sys, times_real   """

    full = Grp(
        19)
    """timestamp, time_elapsed, reason, yg_before, yg_after, yg_allocated, old_before, old_after, old_allocated,
     heap_before, heap_after, heap_allocated, meta_before, meta_after, meta_allocated, duration, times_user, 
     times_sys, times_real"""

    safepoint = Grp(4)
    """timestamp, time_elapsed, threads_were_stopped, stopping_took"""


# region [Metrics processors]

def tz_processor():
    return datetime.strptime(Graphics.full.data[0][0], '%Y-%m-%dT%H:%M:%S.%f%z:').tzinfo


def yg_allocated_processor():
    # return Graphics.minor.data[5][len(Graphics.minor.data[5])-1] #same result
    return max(max(Graphics.minor.data[5]), max(Graphics.full.data[5]))


def yg_peak_processor():
    return max(max(Graphics.minor.data[3]), max(Graphics.full.data[3]))


def og_allocated_processor():
    return max(Graphics.full.data[8])


def og_peak_processor():
    return max(max(Graphics.full.data[6]), max(Graphics.full.data[7]))


def meta_allocated_processor():
    return max(Graphics.full.data[14])


def meta_peak_processor():
    return max(max(Graphics.full.data[12]), max(Graphics.full.data[13]))


def yom_allocated_processor():
    return yg_allocated_processor() + og_allocated_processor() + meta_allocated_processor()  # just an example. useless


# probably should swap it with max(

def yom_peak_processor():
    return yg_peak_processor() + og_peak_processor() + meta_peak_processor()


def heap_allocated_processor():
    return max(max(Graphics.minor.data[8]), max(Graphics.full.data[11]))


def heap_peak_processor():
    return max(max(Graphics.minor.data[6]), max(Graphics.full.data[9]))


def pause_sum_processor():
    return sum(Graphics.full.data[15]) + sum(Graphics.minor.data[9])


def full_pause_avg_processor():
    return sum(Graphics.full.data[15]) / len(Graphics.full.data[15])


def minor_pause_avg_processor():
    return sum(Graphics.minor.data[9]) / len(Graphics.minor.data[9])


def pause_avg_processor():
    return pause_sum_processor() / (len(Graphics.full.data[15]) + len(Graphics.minor.data[9]))


def pause_max_processor():
    return max(max(Graphics.full.data[15]), max(Graphics.minor.data[9]))


def pause_duration_timerange_processor():  # todo: duration, number, percentage table
    total = minor_gc_count_processor() + full_gc_count_processor()
    a = [0] * 12
    b = []
    for i in Graphics.minor.data[9]:
        if i < 1:
            a[int(i * 10)] += 1
        elif i < 5:
            a[10] += 1
        else:
            a[11] += 1

    for i in Graphics.full.data[15]:
        if i < 1:
            a[int(i * 10)] += 1
        elif i < 5:
            a[10] += 1
        else:
            a[11] += 1

    counter = 0

    for value in a[:-2]:
        if value != 0:
            b.append({"duration": int(counter).__str__() + " - " + int(counter + 100).__str__() + "ms",
                      "number": value,
                      "percentage": round(value / total, 4)})
        counter += 100

    value = a[len(a) - 2]
    if value != 0:
        b.append({"duration": "1-5 seconds",
                  "number": value,
                  "percentage": round(value / total, 4)})
    value = a[len(a) - 1]
    if value != 0:
        b.append({"duration": "5+ seconds",
                  "number": value,
                  "percentage": round(value / total, 4)})
    # print(b)
    return b


def minor_gc_count_processor():
    return len(Graphics.minor.data[0])


def minor_gc_reclaimed_processor():
    a = sum(map(sub, Graphics.minor.data[3], Graphics.minor.data[4]))  # yg_after - yg_before
    b = sum(map(sub, Graphics.minor.data[6], Graphics.minor.data[7]))  # heap_before - heap_after
    return [a, b, a - b, a / 1073741824, b / 1073741824]  # todo check


# promotion rate frome here: https://plumbr.io/handbook/gc-tuning-in-practice/premature-promotion


def minor_gc_time_total_processor():
    return sum(Graphics.minor.data[9])


def minor_gc_time_avg_processor():
    return minor_gc_time_total_processor() / len(Graphics.minor.data[0])


def minor_gc_time_std_dev_processor():
    return statistics.stdev(Graphics.minor.data[9])


def minor_gc_time_min_max_processor():
    a = min(Graphics.minor.data[9])
    b = max(Graphics.minor.data[9])
    return [a, b]


def minor_gc_interval_total_processor():
    lastdate = None
    delta = timedelta()
    for date in Graphics.minor.data[0]:
        if lastdate is None:
            lastdate = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f%z:')
        else:
            d = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f%z:')
            delta += d - lastdate
            lastdate = d
    return delta


def minor_gc_interval_average_processor():
    return minor_gc_interval_total_processor() / len(Graphics.minor.data[0])


#

def full_gc_count_processor():
    return len(Graphics.full.data[0])


def full_gc_reclaimed_processor():
    a = sum(map(sub, Graphics.full.data[3], Graphics.full.data[4]))  # yg_after - yg_before
    b = sum(map(sub, Graphics.full.data[9], Graphics.full.data[10]))  # heap_before - heap_after
    b = sum(map(sub, Graphics.full.data[9], Graphics.full.data[10]))  # heap_before - heap_after
    b = sum(map(sub, Graphics.full.data[9], Graphics.full.data[10]))  # heap_before - heap_after
    return [a, b, a - b, a / 1073741824, b / 1073741824]  # todo check


def full_gc_time_total_processor():
    return sum(Graphics.full.data[15])


def full_gc_time_avg_processor():
    return full_gc_time_total_processor() / full_gc_count_processor()


def full_gc_time_std_dev_processor():
    return statistics.stdev(Graphics.full.data[15])


def full_gc_time_min_max_processor():
    a = min(Graphics.full.data[15])
    b = max(Graphics.full.data[15])
    return [a, b]


def full_gc_interval_total_processor():
    lastdate = None
    delta = timedelta()
    for date in Graphics.full.data[0]:
        if lastdate is None:
            lastdate = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f%z:')
        else:
            d = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f%z:')
            delta += d - lastdate
            lastdate = d
    return delta


def full_gc_interval_average_processor():
    return full_gc_interval_total_processor() / len(Graphics.full.data[0])


def full_pause_min_processor():
    return min(Graphics.minor.data[9])


def minor_pause_min_processor():
    return min(Graphics.full.data[15])


def pause_min_processor():
    return min(minor_pause_min_processor(), full_pause_min_processor())


def minor_pause_total_processor():
    return sum(Graphics.minor.data[9])


def full_pause_total_processor():
    return sum(Graphics.full.data[15])


def total_pause_average_processor():
    return (full_pause_total_processor() + minor_pause_total_processor()) / (
            full_gc_count_processor() + minor_gc_count_processor())


def total_pause_interval_average_processor():
    # a=
    return 2  # todo


def total_pause_stdev_processor():
    return statistics.stdev(Graphics.minor.data[9] + Graphics.full.data[15])


def is_last_collection_minor():
    if Graphics.full.data[0][len(Graphics.full.data[0]) - 1] < Graphics.minor.data[0][len(Graphics.minor.data[0]) - 1]:
        return True
    else:
        return False


def total_created_bytes_processor():
    minor_heap_decreased = sum(map(sub, Graphics.minor.data[6], Graphics.minor.data[7]))  # heap_before - heap_after
    full_heap_decreased = sum(map(sub, Graphics.full.data[9], Graphics.full.data[10]))
    if is_last_collection_minor():
        final_heap = Graphics.minor.data[7][len(Graphics.minor.data[7]) - 1]
    else:
        final_heap = Graphics.full.data[10][len(Graphics.full.data[10]) - 1]
    return (minor_heap_decreased + full_heap_decreased + final_heap)  # /(1024*1024*1024)


def promotion_rate_processor(
        minor_grp: Grp = None):  # todo: split 'n move this to where it belongs( Processors.graphics() )
    yg_decreased = map(sub, Graphics.minor.data[3], Graphics.minor.data[4])  # yg_after - yg_before
    total_decreased = map(sub, Graphics.minor.data[6], Graphics.minor.data[7])  # heap_before - heap_after
    promoted = map(sub, yg_decreased, total_decreased)
    promotion_rate = map(truediv, promoted, Graphics.minor.data[9])
    if minor_grp is not None:
        minor_grp.n_of_sets += 1
        minor_grp.data.append(promoted)


def total_promoted_bytes_processor():
    yg_decreased = map(sub, Graphics.minor.data[3], Graphics.minor.data[4])  # yg_after - yg_before
    total_decreased = map(sub, Graphics.minor.data[6], Graphics.minor.data[7])  # heap_before - heap_after
    promoted = map(sub, yg_decreased, total_decreased)
    return sum(promoted)


def average_creation_rate_processor():
    created = total_created_bytes_processor()
    if is_last_collection_minor():
        time_elapsed = Graphics.minor.data[1][len(Graphics.minor.data[1]) - 1]
    else:
        time_elapsed = Graphics.full.data[1][len(Graphics.full.data[1]) - 1]
    return created / float(time_elapsed.__str__().strip(":"))


def average_promotion_rate_processor():
    promoted = total_promoted_bytes_processor()
    if is_last_collection_minor():
        time_elapsed = Graphics.minor.data[1][len(Graphics.minor.data[1]) - 1]
    else:
        time_elapsed = Graphics.full.data[1][len(Graphics.full.data[1]) - 1]
    average_promotion_rate = promoted / float(time_elapsed.__str__().strip(":"))
    return average_promotion_rate


# safe point duration
def threads_were_stopped_total_processor():
    return sum(Graphics.safepoint.data[
                   2])  # todo: rework all stuff including time_total , so it will use last timestamp of all


def threads_were_stopped_avg_processor():
    return sum(Graphics.safepoint.data[2]) / len(Graphics.safepoint.data[2])


def total_program_duration_processor_full():
    a = max(Graphics.safepoint.data[1][len(Graphics.safepoint.data[1]) - 1],
            Graphics.full.data[1][len(Graphics.full.data[1]) - 1],
            Graphics.minor.data[1][len(Graphics.minor.data[1]) - 1])
    last_timestamp = max(Graphics.safepoint.data[0][len(Graphics.safepoint.data[0]) - 1],
                         Graphics.full.data[0][len(Graphics.full.data[0]) - 1],
                         Graphics.minor.data[0][len(Graphics.minor.data[0]) - 1])
    first_timestamp = min(Graphics.safepoint.data[0][0],
                          Graphics.full.data[0][0],
                          Graphics.minor.data[0][0])
    f = datetime.strptime(first_timestamp, '%Y-%m-%dT%H:%M:%S.%f%z:')
    l = datetime.strptime(last_timestamp, '%Y-%m-%dT%H:%M:%S.%f%z:')

    min_dur = min(Graphics.safepoint.data[1][0],
                  Graphics.full.data[1][0],
                  Graphics.minor.data[1][0])
    # delta= timedelta(yea)
    # print(type(l))
    return a, last_timestamp, first_timestamp, l - f, min_dur, (l - f).seconds + min_dur


def total_program_duration_processor():
    return max(Graphics.safepoint.data[1][len(Graphics.safepoint.data[1]) - 1],
               Graphics.full.data[1][len(Graphics.full.data[1]) - 1],
               Graphics.minor.data[1][len(Graphics.minor.data[1]) - 1])


def threads_were_stopped_percentage_processor():
    threads_were_stopped_total_processor()
    pass


def filename_processor():
    return ofname


# endregion


class Processors:

    @staticmethod
    def graphics(line):
        if "threads" in line:
            Graphics.safepoint.put(line[0],  # 0 timestamp
                                   float(line[1].strip(":")),  # 1 time elapsed
                                   line[10],  # threads were stopped
                                   line[15])  # stopping took
        if "secs]" in line:
            if "[Full" in line:
                sex_index = line.index('secs]') - 7  # young
                a = line[sex_index]
                a = a.__str__().split("K->")
                yg_b4 = int(a[0])
                a = a[1].__str__().split("K(")
                yg_after = int(a[0])
                yg_allocated = int(a[1].strip("K)]"))
                sex_index += 2
                a = line[sex_index]
                a = a.__str__().split("K->")
                old_b4 = int(a[0])
                a = a[1].__str__().split("K(")
                old_after = int(a[0])
                old_allocated = int(a[1].strip("K)]"))
                sex_index += 1
                a = line[sex_index]
                a = a.__str__().split("K->")
                heap_b4 = int(a[0])
                a = a[1].__str__().split("K(")
                heap_after = int(a[0])
                heap_allocated = int(a[1].strip("K),"))
                sex_index += 2
                a = line[sex_index]
                a = a.__str__().split("K->")
                meta_b4 = int(a[0])
                a = a[1].__str__().split("K(")
                meta_after = int(a[0])
                meta_allocated = int(a[1].strip("K)],"))
                Graphics.full.put(line[0],  # 0 timestamp
                                  float(line[1].strip(":")),  # 1 time elapsed
                                  line[4],  # 2 reason
                                  yg_b4,  # 3
                                  yg_after,  # 4
                                  yg_allocated,  # 5
                                  old_b4,  # 6
                                  old_after,  # 7
                                  old_allocated,  # 8
                                  heap_b4,  # 9
                                  heap_after,  # 10
                                  heap_allocated,  # 11
                                  meta_b4,  # 12
                                  meta_after,  # 13
                                  meta_allocated,  # 14
                                  float(line[12]),  # 15 duration
                                  line[15].__str__().strip("user=").strip(","),  # 16 times_user
                                  line[16].__str__().strip("sys=").strip(","),  # 17 times_sys
                                  line[17].__str__().strip("real=").strip(","),  # 18 times_real
                                  )

            elif "[GC" in line:
                sex_index = line.index('secs]')
                a = line[sex_index - 3]
                a = a.__str__().split("K->")
                yg_b4 = int(a[0])
                a = a[1].__str__().split("K(")
                yg_after = int(a[0])
                yg_allocated = int(a[1].strip("K)]"))

                reason = line[3]

                a = line[sex_index - 2]
                a = a.__str__().split("K->")
                heap_b4 = int(a[0])
                a = a[1].__str__().split("K(")
                heap_after = int(a[0])
                heap_allocated = int(a[1].strip("K),"))
                Graphics.minor.put(line[0],  # 0 timestamp
                                   float(line[1].strip(":")),  # 1 time elapsed
                                   reason,  # 2 reason
                                   yg_b4,  # 3
                                   yg_after,  # 4
                                   yg_allocated,  # 5
                                   heap_b4,  # 6
                                   heap_after,  # 7
                                   heap_allocated,  # 8
                                   float(line[sex_index - 1]),  # 9 duration
                                   line[sex_index + 2].__str__().strip("user=").strip(","),  # 10 times_user
                                   line[sex_index + 3].__str__().strip("sys=").strip(","),  # 11 times_sys
                                   line[sex_index + 4].__str__().strip("real=").strip(",")  # 12 times_real
                                   )
                pass


class Metrics:
    metrics = []
    # region [Metrics]
    timezone = Metric("Timezone", tz_processor)
    metrics.append(timezone)
    # Jvm Heap size
    yg_allocated = Metric("Young gen: allocated", yg_allocated_processor)
    yg_allocated.legend = " KB"
    metrics.append(yg_allocated)

    yg_peak = Metric("Young gen: peak", yg_peak_processor)
    yg_peak.legend = " KB"
    metrics.append(yg_peak)

    og_allocated = Metric("Old gen: allocated", og_allocated_processor)
    og_allocated.legend = " KB"
    metrics.append(og_allocated)

    og_peak = Metric("Old gen: peak", og_peak_processor)
    metrics.append(og_peak)

    meta_allocated = Metric("Metaspace: allocated", meta_allocated_processor)
    metrics.append(meta_allocated)

    meta_peak = Metric("Metaspace: peak", meta_peak_processor)
    metrics.append(meta_peak)

    yom_allocated = Metric("Young + Old + Meta: allocated", yom_allocated_processor)
    metrics.append(yom_allocated)  # dont use this

    yom_peak = Metric("Young + Old + Meta: peak", yom_peak_processor)  # and this one
    metrics.append(yom_peak)  # as these are just sum of max values

    heap_allocated = Metric("Heap: allocated", heap_allocated_processor)
    metrics.append(heap_allocated)

    heap_peak = Metric("Heap: peak", heap_peak_processor)
    metrics.append(heap_peak)

    pause_avg = Metric("Pause GC time: Average", pause_avg_processor)
    metrics.append(pause_avg)

    pause_max = Metric("Pause GC time: Max", pause_max_processor)
    metrics.append(pause_max)

    pause_duration_timerange = Metric(
        "Pause duration timerange array, split by 100ms range: 0-9 wheres the last one contains > 1 sec values",
        pause_duration_timerange_processor)
    metrics.append(pause_duration_timerange)

    minor_gc_count = Metric("Minor gc: count", minor_gc_count_processor)
    metrics.append(minor_gc_count)

    minor_gc_reclaimed = Metric("Minor gc: reclaimed", minor_gc_reclaimed_processor)
    metrics.append(minor_gc_reclaimed)

    minor_gc_time_total = Metric("Minor gc time: total", minor_gc_time_total_processor)
    metrics.append(minor_gc_time_total)

    minor_gc_time_avg = Metric("Minor gc time: avg", minor_gc_time_avg_processor)
    metrics.append(minor_gc_time_avg)

    minor_gc_time_std_dev = Metric("Minor gc time: standard deviation", minor_gc_time_std_dev_processor)
    metrics.append(minor_gc_time_std_dev)

    minor_gc_time_min_max = Metric("Minor gc time: Min, Max", minor_gc_time_min_max_processor)
    metrics.append(minor_gc_time_min_max)

    minor_gc_interval_average = Metric("Minor gc: average interval", minor_gc_interval_average_processor)
    metrics.append(minor_gc_interval_average)
    #
    full_gc_count = Metric("full gc: count", full_gc_count_processor)
    metrics.append(full_gc_count)

    full_gc_reclaimed = Metric("full gc: reclaimed", full_gc_reclaimed_processor)
    metrics.append(full_gc_reclaimed)

    full_gc_time_total = Metric("full gc time: total", full_gc_time_total_processor)
    metrics.append(full_gc_time_total)

    full_gc_time_avg = Metric("full gc time: avg", full_gc_time_avg_processor)
    metrics.append(full_gc_time_avg)

    full_gc_time_std_dev = Metric("full gc time: standard deviation", full_gc_time_std_dev_processor)
    metrics.append(full_gc_time_std_dev)

    full_gc_time_min_max = Metric("full gc time: Min, Max", full_gc_time_min_max_processor)
    metrics.append(full_gc_time_min_max)

    full_gc_interval_average = Metric("full gc: average interval", full_gc_interval_average_processor)
    metrics.append(full_gc_interval_average)

    total_pause_average = Metric("Total GC pause: average", total_pause_average_processor)
    metrics.append(total_pause_average)

    total_pause_stdev = Metric("Total GC pause: stddev", total_pause_stdev_processor)
    metrics.append(total_pause_stdev)

    total_pause_interval_average = Metric("Total GC pause: average interval", total_pause_interval_average_processor)
    metrics.append(total_pause_interval_average)

    """
    Total: count = full+minor counts
    Reclaimed  = full+minor reclaimed
    time: f+m
    avg_time: new
    stdev: new
    min_max: min(mins), max(maxes)
    interval_avg: new
    
    """
    pause_min = Metric("Pause: min", pause_min_processor)
    metrics.append(pause_min)

    ## object stats:
    total_created_bytes = Metric("Total created, kilobytes:", total_created_bytes_processor)
    metrics.append(total_created_bytes)

    total_promoted_bytes = Metric("Total promoted, kilobytes:", total_promoted_bytes_processor)
    metrics.append(total_promoted_bytes)

    average_creation_rate = Metric("Average creation rate:", average_creation_rate_processor)
    metrics.append(average_creation_rate)

    average_promotion_rate = Metric("Average promotion rate:", average_promotion_rate_processor)
    metrics.append(average_promotion_rate)

    total_program_duration = Metric("Duration:", total_program_duration_processor)
    metrics.append(total_program_duration)

    filename = Metric("Filename:", filename_processor)
    metrics.append(filename)
    # endregion


def clear():
    Graphics.minor = Grp(13)
    Graphics.full = Grp(19)
    Graphics.safepoint = Grp(4)


def main():
    clear()
    with open(fname, 'r') as file:

        for line in file:
            # line = file.readline()
            spline = line.split()
            Processors.graphics(spline)
    # Graphics.full.print(16)
    # Graphics.minor.print(7)
    for a in Metrics.metrics:
        a.process()
        # a.print()

# main()
