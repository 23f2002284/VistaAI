from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from logics.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class TourRequest(Base):
    __tablename__ = "tour_requests"

    request_id = Column(String, primary_key=True, default=generate_uuid)
    preference = Column(String, nullable=True)
    rough_notes = Column(String, nullable=True)
    mode = Column(String, default="Premium")

    rooms = relationship("Room", back_populates="tour_request", cascade="all, delete-orphan")
    final_tour = relationship("FinalTour", back_populates="tour_request", uselist=False, cascade="all, delete-orphan")


class Room(Base):
    __tablename__ = "rooms"

    room_id = Column(String, primary_key=True, default=generate_uuid)
    request_id = Column(String, ForeignKey("tour_requests.request_id"))
    sequence_order = Column(Integer, default=1)
    original_image_path = Column(String, nullable=False)
    room_type = Column(String, nullable=True)
    staging_prompt = Column(String, nullable=True)
    staged_image_path = Column(String, nullable=True)

    tour_request = relationship("TourRequest", back_populates="rooms")
    transition_video = relationship("TransitionVideo", back_populates="room", uselist=False, cascade="all, delete-orphan")
    narration = relationship("Narration", back_populates="room", uselist=False, cascade="all, delete-orphan")


class TransitionVideo(Base):
    __tablename__ = "transition_videos"

    video_id = Column(String, primary_key=True, default=generate_uuid)
    room_id = Column(String, ForeignKey("rooms.room_id"))
    video_path = Column(String, nullable=True)
    duration_seconds = Column(Float, default=4.0)
    model_name = Column(String, default="veo-3.1")

    room = relationship("Room", back_populates="transition_video")
    room_clips = relationship("RoomClip", back_populates="transition_video")


class Narration(Base):
    __tablename__ = "narrations"

    narration_id = Column(String, primary_key=True, default=generate_uuid)
    room_id = Column(String, ForeignKey("rooms.room_id"))
    script_text = Column(String, nullable=True)
    audio_path = Column(String, nullable=True)
    audio_duration = Column(Float, default=4.0)
    voice = Column(String, default="Kore")

    room = relationship("Room", back_populates="narration")
    room_clips = relationship("RoomClip", back_populates="narration")


class RoomClip(Base):
    __tablename__ = "room_clips"

    clip_id = Column(String, primary_key=True, default=generate_uuid)
    video_id = Column(String, ForeignKey("transition_videos.video_id"))
    narration_id = Column(String, ForeignKey("narrations.narration_id"))
    clip_path = Column(String, nullable=True)
    overlay_text = Column(String, nullable=True)

    transition_video = relationship("TransitionVideo", back_populates="room_clips")
    narration = relationship("Narration", back_populates="room_clips")


class FinalTour(Base):
    __tablename__ = "final_tours"

    tour_id = Column(String, primary_key=True, default=generate_uuid)
    request_id = Column(String, ForeignKey("tour_requests.request_id"))
    output_path = Column(String, nullable=True)
    transition_type = Column(String, default="crossfade")
    transition_duration = Column(Float, default=0.5)

    tour_request = relationship("TourRequest", back_populates="final_tour")
