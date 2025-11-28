import unittest

import spinner


def frame_dimensions(frame: str) -> tuple[int, int]:
    lines = frame.splitlines()
    height = len(lines)
    width = max(len(line) for line in lines)
    return height, width


class TestFrames(unittest.TestCase):
    def test_chip_frames_same_size(self):
        frames = spinner.chip_spinner().frames
        first_dim = frame_dimensions(frames[0])
        for frame in frames[1:]:
            self.assertEqual(first_dim, frame_dimensions(frame))

    def test_cockroach_frames_same_size(self):
        frames = spinner.cockroach_spinner().frames
        first_dim = frame_dimensions(frames[0])
        for frame in frames[1:]:
            self.assertEqual(first_dim, frame_dimensions(frame))


class TestParsing(unittest.TestCase):
    def test_parse_choice_variants(self):
        self.assertEqual("chip", spinner.parse_choice("chip"))
        self.assertEqual("chip", spinner.parse_choice("C"))
        self.assertEqual("cockroach", spinner.parse_choice("roach"))
        self.assertEqual("cockroach", spinner.parse_choice("R"))

    def test_parse_choice_invalid(self):
        with self.assertRaises(ValueError):
            spinner.parse_choice("invalid")


class FakeWriter:
    def __init__(self):
        self.buffer = []

    def write(self, text: str):
        self.buffer.append(text)

    def flush(self):
        pass

    def joined(self) -> str:
        return "".join(self.buffer)


class TestAnimate(unittest.TestCase):
    def test_animate_runs_requested_iterations(self):
        sp = spinner.chip_spinner()
        writer = FakeWriter()
        spinner.animate(sp, iterations=3, writer=writer, sleep_fn=lambda _: None)
        output = writer.joined()
        self.assertEqual(output.count(spinner.CLEAR_AND_HOME), 3)
        self.assertIn("Press Ctrl+C to stop.", output)


class TestPhraseGenerator(unittest.TestCase):
    def test_unique_phrases(self):
        pg = spinner.PhraseGenerator(["a", "b"], ["c", "d"], "tag")
        phrases = {next(pg) for _ in range(6)}
        self.assertEqual(len(phrases), 6)
        for text in phrases:
            self.assertIn("tag #", text)


if __name__ == "__main__":
    unittest.main()
