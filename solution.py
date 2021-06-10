import pandas as pd

# Point 2
# Since the log files are in a different format, it is necessary to make them compatible with PM4PY before processing them
df_web_server = pd.read_csv("WEB_SERVER.log", sep=' ', header=None)
df_web_server[5] = (df_web_server[5].astype(str) + df_web_server[6].astype(str)).str.strip("[]")
df_web_server[5] = pd.to_datetime(df_web_server[5], format='%d/%b/%Y:%H:%M:%S%z')
df_web_server = df_web_server.drop(labels=[0, 2, 3, 6, 9, 11, 12], axis=1)
df_web_server = df_web_server.rename(columns={1: "IP", 4: "ID", 5: "TIMESTAMP", 7: "REQUEST", 8: "CODE", 10: "URL"})

df_application_server = pd.read_csv("APPLICATION_SERVER.log", sep=' ', header=None)
df_application_server[3] = (df_application_server[3].astype(str) + df_application_server[4].astype(str)).str.strip("[]")
df_application_server[3] = pd.to_datetime(df_application_server[3], format='%d/%b/%Y:%H:%M:%S%z')
df_application_server = df_application_server.drop(labels=[1, 2, 4, 7], axis=1)
df_application_server = df_application_server.rename(columns={0: "IP", 3: "TIMESTAMP", 5: "REQUEST", 6: "CODE"})

df_merged = pd.merge(df_web_server, df_application_server, on=["IP", "TIMESTAMP", "REQUEST", "CODE"])
# In this case I'have used also TIMESTAMP column beacuse after a check I'm sure that there aren't differences
# between timestamps
# df_merged["TIMESTAMP_DIFF"] = (df_merged["TIMESTAMP_y"] - df_merged["TIMESTAMP_x"]).dt.microseconds

print(df_merged)







