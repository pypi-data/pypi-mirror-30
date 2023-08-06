import pandas as pd

from .. import Interpreter as VanillaInterpreter, Time
from ..errors import CraftAiNullDecisionError
from .utils import is_valid_property_value, create_timezone_df, DUMMY_COLUMN_NAME

def decide_from_row(tree, columns, row, timezone_df):
  context = {
    col: row[col] for col in columns if is_valid_property_value(col, row[col])
  }
  # If a timezone_df is provided use it
  # otherwise use the dataframe index timezone
  if isinstance(timezone_df, pd.DataFrame):
    timezone = timezone_df.loc[row.name].values[0]
    context.update({timezone_df.columns[0]: timezone})
  else:
    timezone = row.name.tz
  time = Time(
    t=row.name.value // 10 ** 9, # Timestamp.value returns nanoseconds
    timezone=timezone
  )
  try:
    decision = VanillaInterpreter.decide(tree, [context, time])

    keys, values = zip(*[
      (output + "_" + key, value)
      for output, output_decision in decision["output"].items()
      for key, value in output_decision.items()
    ])

    return pd.Series(data=values, index=keys)
  except CraftAiNullDecisionError as e:
    return pd.Series(data=[e.message], index=["error"])

class Interpreter(VanillaInterpreter):
  @staticmethod
  def decide_from_contexts_df(tree, contexts_df):
    _, configuration, _ = VanillaInterpreter._parse_tree(tree)
    tz_col = [key for key, value in configuration["context"].items()
              if value["type"] == "timezone"]
    if tz_col:
      tz_col = tz_col[0]
    # If a timezone is needed create a timezone dataframe which will
    # store the timezone to use. It can either be the DatetimeIndex
    # timezone or the timezone column if provided.
    timezone_df = None
    columns = contexts_df.columns.tolist()
    if tz_col:
      timezone_df = create_timezone_df(contexts_df, tz_col)
      if tz_col in columns:
        columns.remove(tz_col)
    if not contexts_df.columns.values.size:
      # Add dummy column in order to avoid apply() issue (aka feature)
      # with empty DataFrame.
      # https://github.com/pandas-dev/pandas/issues/16621
      df = contexts_df.copy(deep=True)
      df[DUMMY_COLUMN_NAME] = 0
    else:
      df = contexts_df
    return df.apply(lambda row: decide_from_row(tree,
                                                columns,
                                                row,
                                                timezone_df), axis=1)
