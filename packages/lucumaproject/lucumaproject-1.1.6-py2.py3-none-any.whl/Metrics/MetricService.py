from Metrics import MetricContext

class MetricService:

    def evaluate_metrics(df,interface):
        tables = interface.tables

        if(len(tables)>0):
            for table in tables:
                if(not table.is_load_information):
                    table.load_dataset()
                data_set = table.data_set
                columns = table.columns
                if len(columns) > 0:
                    for row in data_set.rdd.toLocalIterator():
                        metric_context = MetricContext(dict())
                        metric_context.items.update({'row':row})
                        for column in columns:
                            if(column.metric is not None):
                                column.metric.evaluate(row[column.name],metric_context)