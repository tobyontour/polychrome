from __future__ import annotations

from threading import Lock
from uuid import uuid4

from .models.vouch import Vouch, Voucher


class DuplicateVoucherError(Exception):
    """Raised when the same user vouches more than once for a vouch."""


class VouchTracker:
    """Stores vouches and received vouchers in memory."""

    def __init__(self) -> None:
        self._vouches: dict[str, Vouch] = {}
        self._lock = Lock()

    def create_vouch(self, title: str, threshold: int, creator: str) -> Vouch:
        vouch = Vouch(id=str(uuid4()), title=title, threshold=threshold, creator=creator)
        with self._lock:
            self._vouches[vouch.id] = vouch
        return vouch

    def list_vouches(self) -> list[Vouch]:
        with self._lock:
            return sorted(self._vouches.values(), key=lambda vouch: vouch.created_at, reverse=True)

    def get_vouch(self, vouch_id: str) -> Vouch | None:
        with self._lock:
            return self._vouches.get(vouch_id)

    def add_voucher(self, parent_vouch_id: str, vouched_by: str) -> Voucher | None:
        with self._lock:
            vouch = self._vouches.get(parent_vouch_id)
            if vouch is None:
                return None
            if any(voucher.vouched_by == vouched_by for voucher in vouch.vouchers):
                raise DuplicateVoucherError
            voucher = Voucher(vouched_by=vouched_by, parent_vouch_id=parent_vouch_id)
            vouch.vouchers.append(voucher)
            return voucher

    def clear(self) -> None:
        with self._lock:
            self._vouches.clear()


vouch_tracker = VouchTracker()
