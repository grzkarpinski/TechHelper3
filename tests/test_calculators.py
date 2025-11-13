import unittest

from fastapi.testclient import TestClient

from techhelper_fastapi.main import app


class SpeedFeedCalculatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_speed_feed_calculator_success(self):
        response = self.client.post(
            "/calculators/speed-feed",
            data={
                "cutting_speed": "180",
                "spindle_speed": "",
                "feed_per_tooth": "0.2",
                "feed_rate": "",
                "diameter": "20",
                "teeth": "4",
            },
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.text
        self.assertIn("Wyniki obliczeń", body)
        self.assertIn("180", body)  # Vc
        self.assertIn("2865", body)  # n ≈ 2864.8 -> 2865 after zaokrąglenia
        self.assertIn("2292", body)  # F ≈ 2291.8 -> 2292 po zaokrągleniu
        self.assertIn("0.200", body)  # Fz format dla wartości < 1

    def test_speed_feed_calculator_validation_error(self):
        response = self.client.post(
            "/calculators/speed-feed",
            data={
                "cutting_speed": "",
                "spindle_speed": "",
                "feed_per_tooth": "",
                "feed_rate": "",
                "diameter": "",
                "teeth": "",
            },
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 400)
        body = response.text
        self.assertIn("Pole Średnica D jest wymagane.", body)
        self.assertIn("Pole Liczba ostrzy z jest wymagane.", body)

    def test_missing_speed_inputs_error(self):
        response = self.client.post(
            "/calculators/speed-feed",
            data={
                "cutting_speed": "",
                "spindle_speed": "",
                "feed_per_tooth": "0.2",
                "feed_rate": "",
                "diameter": "20",
                "teeth": "4",
            },
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 400)
        body = response.text
        self.assertIn(
            "Podaj prędkość skrawania Vc lub obroty wrzeciona n.",
            body,
        )


if __name__ == "__main__":
    unittest.main()