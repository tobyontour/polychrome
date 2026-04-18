from ..models.commentfile import CommentFile, Post
from datetime import datetime
class CommentRepository:
    def __init__(self):
        self.comment_files: dict[str, CommentFile] = {
            "14": CommentFile(
                keypath="14",
                name="Comment File 1",
                header="This is the header of comment file 1",
                last_change=datetime.now(),
                owner="toby",
                access_groups=["admin"],
                posts=[
                    Post(
                        date=datetime.now(),
                        from_line="1",
                        subject="This is the subject of comment file 1",
                        content="This is the content of comment file 1",
                        author="toby",
                        index=0,
                    ),
                    Post(
                        date=datetime.now(),
                        from_line="1",
                        subject="This is the subject of comment file 2",
                        content="This is the content of comment file 2",
                        author="jane",
                        index=1,
                    )
                ]
            )
        }

    def get_comment_file(self, keypath: str) -> CommentFile | None:
        return self.comment_files.get(keypath)

    def create_comment_file(self, comment_file: CommentFile) -> None:
        self.comment_files[comment_file.keypath] = comment_file

    def update_comment_file(self, comment_file: CommentFile) -> None:
        self.comment_files[comment_file.keypath] = comment_file