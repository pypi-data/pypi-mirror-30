import pandas as pd
import six

DUMMY_COLUMN_NAME = "CraftGeneratedDummy"

def is_valid_property_value(key, value):
  # From https://stackoverflow.com/a/19773559
  # https://pythonhosted.org/six/#six.text_type for unicode in Python 2
  return key != DUMMY_COLUMN_NAME and \
         ( \
           (not hasattr(value, "__len__") \
            or isinstance(value, (str, six.text_type))) \
           and pd.notnull(value) \
         )

# Helper
def create_timezone_df(df, name):
  timezone_df = pd.DataFrame(index=df.index)
  if name in df.columns:
    timezone_df[name] = df[name].fillna(method="ffill")
  else:
    timezone_df[name] = df.index.strftime("%z")
  return timezone_df
