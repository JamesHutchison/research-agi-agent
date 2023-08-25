import textwrap

from megamock import Mega, MegaMock

from DeepResearchTool.deep_research.summary_generator import SummaryGenerator


class TestDeepResearchWriterTool:
    class TestGenerateMarkdownPrompt:
        def test_is_dedented(self):
            mock = MegaMock.it(SummaryGenerator)
            mock._format_topic = lambda topic: f"formatted {topic}"
            Mega(mock._generate_markdown_prompt).use_real_logic()
            generated_prompt = mock._generate_markdown_prompt(
                user_query="test query",
                topics=[
                    {
                        "name": "test topic",
                        "description": "test description",
                        "relevant_because": "test relevant because",
                        "notes_file": "test notes file",
                    }
                ],
            )

            # ensure it is dedented
            for line in generated_prompt.splitlines():
                # TODO: fails because logic isn't implemented
                assert not line.startswith("  ")

    class TestFormatTopic:
        def test_formats_topic(self):
            mock = MegaMock.it(SummaryGenerator, spec_set=False)
            mock._notes_getter = lambda notes_file: f"notes from {notes_file}"
            Mega(mock._format_topic).use_real_logic()
            formatted_topic = mock._format_topic(
                {
                    "name": "test topic",
                    "description": "test description",
                    "relevant_because": "test relevant because",
                    "notes_file": "test_notes_file.json",
                }
            )

            assert textwrap.dedent(formatted_topic) == textwrap.dedent(
                """
                    Topic name: test topic
                    Topic description: test description
                    Relevant because: test relevant because
                    Notes: notes from test_notes_file.json
            """
            )

    class TestGetMarkdownSummary:
        def test_takes_prompt_and_plugs_it_into_chat(self) -> None:
            pass  # TODO
