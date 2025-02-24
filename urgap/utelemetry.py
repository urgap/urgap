

from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
)



class UTelemetry:

    trace_was_initialized = False
    metric_was_initialized = False

        self.trace_tree = {}
        self.span_lookup = {}
        self.counters = {}
        self._meter = None
        self._tracer = None

    @property
    def otlp_url(self) -> str | None:

    @property
    def otlp_type(self) -> str | None:

    @property
    def tracing_enabled(self) -> bool:

        """
        return self.otlp_type is not None

    @property
    def meter(self) -> metrics.Meter | None:

        Returns:
        """
        if self._meter is None and self.tracing_enabled is True:
            self._meter = self.init_meter()
        return self._meter

    @property
    def tracer(self) -> trace.Tracer | None:

        Returns:
        """
        if self._tracer is None and self.tracing_enabled is True:
            self._tracer = self.init_tracer()
        return self._tracer

    @staticmethod
    def init_meter(self) -> metrics.Meter:
        if UTelemetry.metric_was_initialized is False:
            if self.otlp_type == "OTLP":
                exporter = OTLPMetricExporter(endpoint=self.otlp_url)
            elif self.otlp_type == "Console":
                exporter = ConsoleMetricExporter()
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
            elif self.otlp_type == "Console":
                exporter = ConsoleSpanExporter()
            elif self.otlp_type == "AZ-Insights":
                )
                exporter = AzureMonitorTraceExporter.from_connection_string(
                )
            else:
            trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(exporter))


        """


        Args:
        """
        for counter_name in counter_name_list:
            self.increase_counter(counter_name, count=count)

    def init_span(
        self,
        span_context: list,
        spankind: SpanKind = None,
    ) -> trace.Span:
        """Start and return a new OpenTelemetry span.

        Args:

        Returns:
        """
        current_tree = self.trace_tree
        parent_context = None

        for n, name in enumerate(span_context):
            if n == 0:
                kind = SpanKind.SERVER
            else:
            if name not in current_tree:
                new_span = self.tracer.start_span(
                )
                if self.otlp_type == "AZ-Insights":
                    new_span.set_attribute("db.system", "Microsoft.ServiceBus")
                if attributes is not None:
                    new_span.set_attributes(attributes)

                new_context = trace.set_span_in_context(new_span, parent_context)

                current_tree[name] = {
                    "span": new_span,
                    "context": new_context,
                    "children": {},
                    "path": span_context[: n + 1][:],
                    "name": name,
                    "parent_span_context": span_context[:n][:],
                }
                UTelemetry.started_spans.append(new_span)
                self.span_lookup["<|>".join(span_context[: n + 1])] = current_tree[name]

            parent_context = current_tree[name]["context"]
            final_span = current_tree[name]["span"]
            current_tree = current_tree[name]["children"]

        if event is not None:
            final_span.add_event(event)
        return final_span

    def add_span_event(
        self,
        nested_span_list: list,
        event: str,

        Args:
        """
        if span is None:
        else:
            span.add_event(event)

    def add_span_events(
        self,
        nested_span_list: list,
        events: list,

        Args:
        """
        for event in events:
            if span is None:
            else:
                span.add_event(event)

    def set_span_attribute(
        self,
        nested_span_list: list,
        key: str,
        value: str,

        Args:
        """
        if span is None:
        else:
            span.set_attribute(key, value)

    def set_span_attributes(
        self,
        nested_span_list: list,
        attributes: dict,

        Args:
        """
        if span is None:
        else:
            span.set_attributes(attributes)

    def set_span_status(
        self,
        nested_span_list: list,
        status: StatusCode,

        Args:
        """
        if span is None:
        else:
            span.set_status(status)

        container = self._find_container(nested_span_list)
        if container is None:

    def _find_container(self, nested_span_list: list) -> dict:
        lookup_key = "<|>".join(nested_span_list)
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
        self.span_lookup.pop("<|>".join(node["path"]))
        parent_container = self._find_container(node["parent_span_context"])
        if parent_container is not None:
            parent_container["children"].pop(node["name"])
        else:
            self.trace_tree.pop(node["name"])

        for span in UTelemetry.started_spans[::-1]:
            if span.is_recording() is True:
                span.end()
        UTelemetry.started_spans = []
        self.span_lookup = {}
