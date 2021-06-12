import pandas as pd
import matplotlib.pyplot as plt
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.objects.log.util import interval_lifecycle
from pm4py.algo.filtering.log.variants import variants_filter
from math import sqrt

## Point 2
# Since the log files are in a different format, it is necessary to make them compatible with PM4PY before processing them
df_web_server = pd.read_csv("WEB_SERVER.log", sep=' ', header=None)
df_web_server[5] = (df_web_server[5] + df_web_server[6]).str.strip("[]")
df_web_server[5] = pd.to_datetime(df_web_server[5], format='%d/%b/%Y:%H:%M:%S%z')
df_web_server = df_web_server.drop(labels=[0, 2, 3, 6, 9, 11, 12], axis=1)
df_web_server = df_web_server.rename(columns={1: "IP", 4: "ID", 5: "TIMESTAMP", 7: "REQUEST", 8: "CODE", 10: "URL"})

# print(df_web_server)

df_application_server = pd.read_csv("APPLICATION_SERVER.log", sep=' ', header=None)
df_application_server[3] = (df_application_server[3] + df_application_server[4]).str.strip("[]")
df_application_server[3] = pd.to_datetime(df_application_server[3], format='%d/%b/%Y:%H:%M:%S%z')
df_application_server = df_application_server.drop(labels=[1, 2, 4, 7], axis=1)
df_application_server = df_application_server.rename(columns={0: "IP", 3: "TIMESTAMP", 5: "REQUEST", 6: "CODE"})

# print(df_application_server)

df_joined = df_web_server.join(df_application_server["TIMESTAMP"], lsuffix="_WS", rsuffix="_AS")
df_joined["TIME_DELTA"] = (df_joined["TIMESTAMP_AS"] - df_joined["TIMESTAMP_WS"]) / pd.Timedelta(seconds=1)

# print(df_joined)

my_col = [x for x in range(50)]
df_database_server = pd.read_csv("DATABASE_SERVER.log", sep=' ', header=None, names=my_col)
df_database_server = df_database_server.fillna('')
df_database_server[0] = df_database_server[0] + ':' + df_database_server[1] + "+0200"
df_database_server[0] = pd.to_datetime(df_database_server[0], format='%Y-%m-%d:%H:%M:%S.%f%z')

for i in range(6, 17):
    df_database_server[5] = df_database_server[5] + ' ' + df_database_server[i]

del_col = [1, 2, 6]
del_col.extend([n for n in range(7, 50)])
df_database_server = df_database_server.drop(labels=del_col, axis=1)
df_database_server = df_database_server.rename(columns={0: "TIMESTAMP", 3: "ID", 4: "DATABASE", 5: "OPERATION"})
df_database_server = df_database_server[df_database_server.DATABASE == "postgres@infinity41_sp27p"].reset_index()

# print(df_database_server)

## Point 3
size = len(df_database_server["TIMESTAMP"])
db_delta_times = []
db_timestamps = []
for n in range(0, size, 15):
    try:
        last_op = df_database_server.at[n+15, 'TIMESTAMP']
    except:
        last_op = df_database_server.at[size-1, "TIMESTAMP"]
    first_op = df_database_server.at[n, "TIMESTAMP"]
    time_delta = (last_op - first_op) / pd.Timedelta(seconds=1)
    db_delta_times.append(time_delta)
    db_timestamps.append(first_op)


df_joined["TIME_DELTA_DB"] = db_delta_times[:len(df_joined)]
df_joined["TIMESTAMP_DB"] = db_timestamps[:len(df_joined)]

# print(df_joined)

#Point 4
print(df_joined.describe())

plt.subplot(2, 1, 1)
plt.plot(df_joined.index, df_joined["TIME_DELTA_DB"])
plt.title("Db time delta linechart")

plt.subplot(2, 1, 2)
plt.scatter(df_joined.index, df_joined["TIME_DELTA_DB"])
plt.xlabel("Request number")
plt.ylabel("Time delta")
plt.title("Db time delta scatter chart")

# plt.show()

#Remove outliers\
df_joined_size = len(df_joined)
df_joined = df_joined[df_joined.TIME_DELTA_DB < 5]
print("\nPercentage of overdue cases {0:.2g}%\n".format((df_joined_size - len(df_joined)) / size * 100))

print(df_joined.describe())

## Point 5
df_joined["ID"] = df_joined["ID"].astype(str)
df_joined = df_joined.rename(columns={"ID": "case:concept:name", "REQUEST": "concept:name", "TIMESTAMP_DB": "time:timestamp"})
parameters = {log_converter.Variants.TO_EVENT_LOG.value.Parameters.CASE_ID_KEY: 'case:concept:name'}
event_log = log_converter.apply(df_joined, parameters=parameters, variant=log_converter.Variants.TO_EVENT_LOG)

# print(event_log)

event_log = interval_lifecycle.assign_lead_cycle_time(event_log)

# print("\nPercentile below the safe performance score 3 sec {}%".format(count / ))

variants = variants_filter.get_variants(event_log)

print('\nEvents: {} - Cases: {} - Variants: {}'.format(df_joined_size, len(event_log), len(variants)))

def performance_analysis(variants):
    variants_scores = {}
    count = 0
    for key, value in variants.items():
        variants_scores[key] = 0
        for event in value[0]:
            variants_scores[key] += event["TIME_DELTA_DB"]
        
    performance_drop_variant = max(variants_scores, key=variants_scores.get)

    performance_drop_value = variants_scores[performance_drop_variant]

    print("\n{0:.2g} is the most variant performance drop".format(performance_drop_value))

    plt2 = plt.figure()
    ax1 = plt2.add_subplot(111)
    ax1.plot([x for x in range(len(variants_scores))], variants_scores.values())
    # plt.show()

    count = 0
    for value in variants_scores.values():
        if value < 3:
            count += 1

    print("\nPercentile under 3 sec time delta db {:.2f}%\n".format(count / len(variants_scores) * 100))

    # Remove the variant from the dictionary for the later comparison
    for key, value in variants_scores.items():
        if value == performance_drop_value:
            del variants_scores[key]
            break

    return {0: performance_drop_value, "values": list(variants_scores.values())}

performance_drop = performance_analysis(variants)

#Filter most common variants
filtered_log = variants_filter.filter_log_variants_percentage(event_log, percentage=0.5)
# print(len(filtered_log))

variants_filtered = variants_filter.get_variants(filtered_log)
# print(len(variants_filtered))

performance_analysis(variants_filtered)

## Point 6
for n in range(10):
    x = performance_drop[0]
    y = performance_drop["values"]
    z = (performance_drop[0] - performance_drop["values"][n])/sqrt(performance_drop[0] + performance_drop["values"][n])
    if z > 1.96:
        print("Comparing most performance drop variant with variant number {} differences are significantly important".format(n+1))

## Point 7

















