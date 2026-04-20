import urllib.request

from google.transit import gtfs_realtime_pb2


def realtime(feed_url: str):
    with urllib.request.urlopen(feed_url) as response:
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.read())

    delays = []
    for entity in feed.entity:
        if entity.HasField("trip_update"):
            trip_id = entity.trip_update.trip.trip_id
            for stop in entity.trip_update.stop_time_update:
                delay = stop.arrival.delay
                delays.append({"trip_id": trip_id, "delay": delay})
    return delays
