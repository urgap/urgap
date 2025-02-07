
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)



class UTelemetry:

    trace_was_initialized = False
    metric_was_initialized = False

        self.trace_tree = {}
        self.span_lookup = {}
        self.counters = {}

    def init_meter(self) -> metrics.Meter:
        if UTelemetry.metric_was_initialized is False:
            if self.otlp_type == "OTLP":
                exporter = OTLPMetricExporter(endpoint=self.otlp_url)
            elif self.otlp_type == "AZ-Insights":
                )
                exporter = AzureMonitorMetricExporter.from_connection_string(
                )
            else:
            metrics.set_meter_provider(
                MeterProvider(
                    metric_readers=[
                        PeriodicExportingMetricReader(
                            exporter,
                            export_interval_millis=5000,
            )
            UTelemetry.metric_was_initialized = True

    def init_tracer(self) -> trace.Tracer:
        if UTelemetry.trace_was_initialized is False:
            trace.set_tracer_provider(
                TracerProvider(
                    resource=Resource.create(
                        {
                    ),
            )
            if self.otlp_type == "OTLP":
                exporter = OTLPSpanExporter(
                )
            elif self.otlp_type == "AZ-Insights":
                )
                exporter = AzureMonitorTraceExporter.from_connection_string(
                )
            else:
            trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(exporter))


        """

    def init_span(
        self,
    ) -> trace.Span:
        """Start and return a new OpenTelemetry span.

        Args:

        Returns:
        """
        current_tree = self.trace_tree
        parent_context = None

            if name not in current_tree:
                new_context = trace.set_span_in_context(new_span, parent_context)

                current_tree[name] = {
                    "span": new_span,
                    "context": new_context,
                    "children": {},
                }
                UTelemetry.started_spans.append(new_span)

            parent_context = current_tree[name]["context"]
            final_span = current_tree[name]["span"]
            current_tree = current_tree[name]["children"]

        if event is not None:
            final_span.add_event(event)
        return final_span

        self,
        nested_span_list: list,
        event: str,

        Args:
        """
        if span is None:
        else:
            span.add_event(event)

        self,
        nested_span_list: list,
        events: list,

        Args:
        """
        for event in events:
            if span is None:
            else:
                span.add_event(event)

        self,
        nested_span_list: list,
        key: str,
        value: str,

        Args:
        """
        if span is None:
        else:
            span.set_attribute(key, value)

        self,
        nested_span_list: list,
        attributes: dict,

        Args:
        """
        if span is None:
        else:
            span.set_attributes(attributes)

        container = self._find_container(nested_span_list)
        if container is None:

    def _find_container(self, nested_span_list: list) -> dict:
        container = None
            container = self.span_lookup[lookup_key]
        return container


        Args:
        """
        container = self._find_container(nested_span_list)
        if container is not None:
            self._close_node_recursive(container)
        for child in list(node["children"].values()):
            self._close_node_recursive(child)
        node["span"].end()

        for span in UTelemetry.started_spans[::-1]:
            if span.is_recording() is True:
                span.end()
        UTelemetry.started_spans = []
        self.span_lookup = {}