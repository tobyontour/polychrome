from ..models.commentfile import CommentFile
import os
import json

class CommentRepository:
    def __init__(self, base_path: str):
        self.base_path = base_path

    def get_comment_file(self, keypath: str) -> CommentFile | None:
        if not os.path.exists(os.path.join(self.base_path, f"{keypath}.json")):
            return None
        with open(os.path.join(self.base_path, f"{keypath}.json"), "r") as f:
            return CommentFile.model_validate(json.load(f))

    def create_comment_file(self, comment_file: CommentFile) -> None:
        with open(os.path.join(self.base_path, f"{comment_file.keypath}.json"), "w") as f:
            f.write(comment_file.model_dump_json())

    def update_comment_file(self, comment_file: CommentFile) -> None:
        with open(os.path.join(self.base_path, f"{comment_file.keypath}.json"), "w") as f:
            f.write(comment_file.model_dump_json())