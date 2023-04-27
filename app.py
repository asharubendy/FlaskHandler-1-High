import json

from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
import boto3
import pymsteams

app = Flask(__name__)


def createMessage(messageDict):
    teamsMessage = pymsteams.connectorcard(
        "teamsWebhook")
    teamsMessage.title("ALERT: A NEW HIGH PRIORITY BUG HAS BEEN FOUND!")
    teamsMessage.text("Calling all DevOps Engineers!!")
    messageSection = pymsteams.cardsection()
    messageSection.title(f"Title: {messageDict['bug_title']}")
    messageSection.text(f"Description: {messageDict['bug_desc']}")
    messageSection.addImage(
        "https://w7.pngwing.com/pngs/1006/882/png-transparent-insect-bed-bug-software-bug-computer-icons-insect"
        "-animals-computer-black-thumbnail.png")
    teamsMessage.addSection(messageSection)
    teamsMessage.send()


@app.route("/message", methods=['POST'])
def consumeMessages():
    if request.method == 'POST':
        createMessage(json.loads(request.json))
    else:
        sqs = boto3.resource('sqs')
        # Get the queue
        queue = sqs.get_queue_by_name(QueueName='HighPriority')
        # Process messages by printing out body and optional author name
        for message in queue.receive_messages():
            print(message.body)
            createMessage(json.loads(message.body))
            message.delete()


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=consumeMessages, trigger="interval", seconds=10)
    scheduler.start()
    app.run()
