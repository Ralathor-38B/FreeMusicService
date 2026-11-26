import os
from filecmp import cmp
from pathlib import Path
from shutil import copyfile

from pydantic import ValidationError
from sqlalchemy.orm import Session

from models import Albums, Bands, Musicians, Songs, Users
from schemas import RegisterRequest
from security import hash_password


def seed_database(connection):
    source = Path(__file__).parent / "media"
    media = Path(os.environ["MEDIA_DIR"])
    with Session(connection) as db, db.begin():
        for login, level, variable in [
            ("CoolLog56", 2, "COOLLOG56_PASSWORD"),
            ("Log42", 1, "LOG42_PASSWORD"),
        ]:
            password = os.getenv(variable)
            if not password:
                raise ValueError(f"Для новой базы задайте {variable} в .env")
            email = f"{login.lower()}@example.org"
            try:
                RegisterRequest(login=login, email=email, password=password)
            except ValidationError:
                raise ValueError(f"Пароль {variable} не соответствует правилам регистрации") from None
            db.add(Users(username=login.lower(), email=email,
                         password_hash=hash_password(password), access=level))

        for artist, album, tracks in [
            (Bands(name="Demo Ensemble"), "Signal Sessions", [
                ("Morning Signal", "morning.mp3", 12, 0, "Electronic"),
                ("Evening Signal", "evening.mp3", 12, 1, "Electronic"),
            ]),
            (Bands(name="System of a Down"), "Пасхалка", [("Boom!", "boom.mp3", 135, 2, None)]),
            (Musicians(first_name="Слава КПСС", last_name="", stage_name="Слава КПСС"),
             "Пасхалка", [("Греть гоев", "gret-goev.mp3", 152, 2, None)]),
            (Musicians(first_name="six before", last_name="", stage_name="six before"),
             "Пасхалка", [("SHAMAN", "SHAMAN.mp3", 30, 0, None)]),
            (Bands(name="ILLIT"), "Пасхалка", [
                ("You're Under Arrest", "youre-under-arrest.mp3", 182, 1, None),
            ]),
        ]:
            record = Albums(title=album)
            artist.albums.append(record)
            db.add(artist)
            for number, (title, name, duration, access, genre) in enumerate(tracks, 1):
                target = media / name
                if target.exists():
                    if not cmp(source / name, target, shallow=False):
                        raise ValueError(f"В томе уже есть другой файл {name}")
                else:
                    temporary = target.with_suffix(".mp3.tmp")
                    copyfile(source / name, temporary)
                    temporary.replace(target)
                record.songs.append(Songs(title=title, track_number=number, genre=genre,
                                          file_path=name, duration_seconds=duration, access=access))
