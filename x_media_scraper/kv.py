import os.path, json, pathlib
from typing import Any
from sqlalchemy import create_engine, select, String
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column


class KV:
    class Base(DeclarativeBase):
        pass
    class Entry(Base):
        __tablename__ = "data"

        k: Mapped[str] = mapped_column(String, primary_key=True, index=True)
        v: Mapped[str] = mapped_column(String, nullable=False)

        def __repr__(self) -> str:
            return f'Entry(key={self.k!r}, value={self.v!r})'


    def __init__(self, path: str):
        pathlib.Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
        self._engine = create_engine('sqlite:///'+os.path.realpath(path), echo=False)
        KV.Entry.metadata.create_all(self._engine)

    def is_empty(self) -> bool:
        with Session(self._engine) as session:
            return session.execute(select(KV.Entry).limit(1)).scalar() is None

    def get_value(self, k: str) -> Any:
        with Session(self._engine) as session:
            v = session.execute(select(KV.Entry.v).where(KV.Entry.k == k)).scalar()
            if v is not None:
                try:
                    d = json.loads(v)
                    return d
                except:
                    return v
            return None

    def _set_value(self, session: Session, k: str, v: Any) -> None:
        if type(v) is list or type(v) is dict:
            v = json.dumps(v)
        rec = KV.Entry(k=k, v=v)
        session.merge(rec)

    def set_value(self, k: str, v: Any) -> None:
        with Session(self._engine) as session:
            self._set_value(session, k, v)
            session.commit()

    def set_many(self, kv_list: list[tuple[str,Any]]) -> None:
        with Session(self._engine) as session:
            for k,v in kv_list:
                self._set_value(session, k, v)
            session.commit()
