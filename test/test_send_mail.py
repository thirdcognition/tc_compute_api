from source.helpers.communication import send_new_shows_email_task


def test_send_email():
    email = "markus@thirdcognition.com"
    panels = ["test"]
    send_new_shows_email_task(email, panels)


if __name__ == "__main__":
    test_send_email()
