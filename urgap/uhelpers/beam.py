




        Args:
        """
        self.ready = False
        self.window = beam.transforms.window.GlobalWindow()
        self.unode = None

        if self._check_input(unode=unode, urd=urd):
            self.ready = True


        Args:

        Returns:
        """
        input_is_ok = True
            input_is_ok = False
            input_is_ok = False
            )
        return input_is_ok


        """Execute before a bundle starts."""


        Args:

        Yields:
        """
        if self.ready is True:







    Args:

    Returns:
    """
    from apache_beam.runners.interactive.display import pipeline_graph

    s = pipeline_graph.PipelineGraph(pipeline).get_dot()
    net = Network(
        width="100%",
        directed=True,
        font_color="white",
    )
    net.use_DOT = True
    net.dot_lang = " ".join(s.split("\n"))
    net.dot_lang = net.dot_lang.replace('"', '\\"')
    net.dot_lang = net.dot_lang.replace("fontcolor=blue", "fontcolor=white")
    return net