import numpy as np
import pandas as pd

# Point 2
# Since the log files are in a different format, it is necessary to make them compatible with PM4PY before processing them
df_web_server = pd.read_csv("WEB_SERVER.log", sep=' ', header=None)
df_web_server[5] = (df_web_server[5] + df_web_server[6]).str.strip("[]")
df_web_server[5] = pd.to_datetime(df_web_server[5], format='%d/%b/%Y:%H:%M:%S%z')
df_web_server = df_web_server.drop(labels=[0, 2, 3, 6, 9, 11, 12], axis=1)
df_web_server = df_web_server.rename(columns={1: "IP", 4: "ID", 5: "TIMESTAMP", 7: "REQUEST", 8: "CODE", 10: "URL"})

df_application_server = pd.read_csv("APPLICATION_SERVER.log", sep=' ', header=None)
df_application_server[3] = (df_application_server[3] + df_application_server[4]).str.strip("[]")
df_application_server[3] = pd.to_datetime(df_application_server[3], format='%d/%b/%Y:%H:%M:%S%z')
df_application_server = df_application_server.drop(labels=[1, 2, 4, 7], axis=1)
df_application_server = df_application_server.rename(columns={0: "IP", 3: "TIMESTAMP", 5: "REQUEST", 6: "CODE"})

df_merged = pd.merge(df_web_server, df_application_server, on=["IP", "TIMESTAMP", "REQUEST", "CODE"])
# In this case I'have used also TIMESTAMP column beacuse after a check I'm sure that there aren't differences
# between timestamps
# df_merged["TIMESTAMP_DIFF"] = (df_merged["TIMESTAMP_y"] - df_merged["TIMESTAMP_x"]).dt.microseconds

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
df_database_server = df_database_server[df_database_server.DATABASE == "postgres@infinity41_sp27p"]






