from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from learning_unit_experience import (
    LearningUnitExperienceError,
    load_learning_path_directory,
    load_learning_unit,
)

ROOT = Path(__file__).resolve().parents[1]
PATH_ID = "system-architect-checkin"
MANIFEST_RELATIVE = Path("data/learning-paths/system-architect-checkin-v1.json")
CONTENT_RELATIVE = Path("content/learning-units/system-architect-checkin")


class LearningUnitExperienceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / MANIFEST_RELATIVE.parent).mkdir(parents=True)
        (self.root / "taxonomy").mkdir()
        shutil.copyfile(ROOT / MANIFEST_RELATIVE, self.root / MANIFEST_RELATIVE)
        shutil.copyfile(ROOT / "taxonomy/taxonomy.json", self.root / "taxonomy/taxonomy.json")
        shutil.copytree(ROOT / CONTENT_RELATIVE, self.root / CONTENT_RELATIVE)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_merge_items_keep_independent_identity_and_topic_association(self) -> None:
        first = load_learning_unit(PATH_ID, "checkin-001", project_root=self.root)
        second = load_learning_unit(PATH_ID, "checkin-002", project_root=self.root)

        self.assertEqual(first.item_id, "checkin-001")
        self.assertEqual(second.item_id, "checkin-002")
        self.assertNotEqual(first.title, second.title)
        self.assertEqual(first.topic_ids, ("SOFTWARE.ENGINEERING.PROCESS",))
        self.assertEqual(second.topic_ids, first.topic_ids)
        self.assertIn("# 软件工程：生命周期与基本要素", first.content_markdown)
        self.assertNotIn("content_version:", first.content_markdown)

    def test_split_is_one_unit_with_all_topic_labels(self) -> None:
        unit = load_learning_unit(PATH_ID, "checkin-005", project_root=self.root)

        self.assertEqual(unit.item_id, "checkin-005")
        self.assertEqual(unit.mapping_status, "split")
        self.assertEqual(unit.topic_ids, (
            "SOFTWARE.ENGINEERING.PROCESS",
            "SOFTWARE.ENGINEERING.TESTING",
        ))
        self.assertEqual([topic.name for topic in unit.topics], ["软件过程与开发方法", "软件测试"])

    def test_exact_unit_has_a_readable_topic_label(self) -> None:
        unit = load_learning_unit(PATH_ID, "checkin-006", project_root=self.root)
        self.assertEqual(unit.mapping_status, "exact")
        self.assertEqual([topic.name for topic in unit.topics], ["构件与组件技术"])

    def test_unmapped_unit_remains_readable_without_a_fabricated_topic(self) -> None:
        unit = load_learning_unit(PATH_ID, "checkin-032", project_root=self.root)
        self.assertEqual(unit.mapping_status, "unmapped")
        self.assertEqual(unit.topic_ids, ())
        self.assertEqual(unit.topics, ())
        self.assertIn("# 可观测性：指标、日志与链路追踪", unit.content_markdown)

    def test_non_learning_item_is_unavailable_even_without_markdown(self) -> None:
        with self.assertRaises(LearningUnitExperienceError) as caught:
            load_learning_unit(PATH_ID, "checkin-020", project_root=self.root)
        self.assertEqual(caught.exception.category, "not_a_learning_unit")
        self.assertFalse((self.root / CONTENT_RELATIVE / "checkin-020.md").exists())

    def test_unknown_path_and_item_are_not_used_as_filesystem_paths(self) -> None:
        for path_id, item_id, category in (
            ("../../etc", "passwd", "unknown_learning_path"),
            (PATH_ID, "../../../../etc/passwd", "unknown_learning_unit"),
            (PATH_ID, "checkin-999", "unknown_learning_unit"),
        ):
            with self.subTest(path_id=path_id, item_id=item_id):
                with self.assertRaises(LearningUnitExperienceError) as caught:
                    load_learning_unit(path_id, item_id, project_root=self.root)
                self.assertEqual(caught.exception.category, category)

    def test_frontmatter_identity_fields_fail_closed(self) -> None:
        fields = (
            ("path_id: system-architect-checkin", "path_id: other-path"),
            ("path_version: 1.0.0", "path_version: 2.0.0"),
            ("item_id: checkin-001", "item_id: checkin-002"),
            ("order: 1", "order: 2"),
            ("status: merge", "status: exact"),
            ("confidence: high", "confidence: low"),
            ("SOFTWARE.ENGINEERING.PROCESS", "SOFTWARE.ENGINEERING.TESTING"),
        )
        original = (self.root / CONTENT_RELATIVE / "checkin-001.md").read_text(encoding="utf-8")
        for old, new in fields:
            with self.subTest(field=old):
                self.assertIn(old, original)
                (self.root / CONTENT_RELATIVE / "checkin-001.md").write_text(
                    original.replace(old, new, 1), encoding="utf-8"
                )
                with self.assertRaises(LearningUnitExperienceError) as caught:
                    load_learning_unit(PATH_ID, "checkin-001", project_root=self.root)
                self.assertEqual(caught.exception.category, "invalid_learning_unit")
        (self.root / CONTENT_RELATIVE / "checkin-001.md").write_text(original, encoding="utf-8")

    def test_malformed_or_duplicate_frontmatter_fails_closed(self) -> None:
        path = self.root / CONTENT_RELATIVE / "checkin-001.md"
        original = path.read_text(encoding="utf-8")
        malformed = original.replace("mapping:\n", "mapping: [\n", 1)
        path.write_text(malformed, encoding="utf-8")
        with self.assertRaises(LearningUnitExperienceError):
            load_learning_unit(PATH_ID, "checkin-001", project_root=self.root)

        path.write_text(original.replace(
            "path_id: system-architect-checkin\n",
            "path_id: other-path\npath_id: system-architect-checkin\n",
            1,
        ), encoding="utf-8")
        with self.assertRaises(LearningUnitExperienceError):
            load_learning_unit(PATH_ID, "checkin-001", project_root=self.root)

    def test_manifest_order_drives_directory_and_non_learning_is_preserved(self) -> None:
        directory = load_learning_path_directory(PATH_ID, project_root=self.root)
        self.assertEqual(directory.path_id, PATH_ID)
        self.assertEqual(directory.version, "1.0.0")
        self.assertEqual(directory.path_status, "draft")
        self.assertEqual(len(directory.items), 112)
        self.assertEqual([item.order for item in directory.items], list(range(1, 113)))
        self.assertEqual(directory.items[0].title, "软件工程：生命周期与基本要素")
        self.assertEqual(directory.items[19].kind, "non_learning")
        self.assertEqual(directory.items[19].title, "休息")
        self.assertEqual(directory.items[31].mapping_status, "unmapped")
        self.assertEqual(directory.items[31].kind, "learning_unit")
        self.assertFalse((self.root / CONTENT_RELATIVE / "checkin-020.md").exists())
        model = asdict(directory)
        for forbidden in ("progress", "completed", "mastery", "review_due", "completion"):
            self.assertNotIn(forbidden, model)
        for item in model["items"]:
            for forbidden in ("progress", "completed", "mastery", "review_due", "completion"):
                self.assertNotIn(forbidden, item)

    def test_previous_and_next_follow_manifest_order_and_skip_non_learning(self) -> None:
        cases = (
            ("checkin-001", None, "checkin-002"),
            ("checkin-050", "checkin-049", "checkin-051"),
            ("checkin-019", "checkin-018", "checkin-021"),
            ("checkin-021", "checkin-019", "checkin-022"),
            ("checkin-025", "checkin-024", "checkin-027"),
            ("checkin-027", "checkin-025", "checkin-028"),
            ("checkin-032", "checkin-031", "checkin-033"),
            ("checkin-005", "checkin-004", "checkin-006"),
            ("checkin-112", "checkin-111", None),
        )
        for item_id, previous, following in cases:
            with self.subTest(item_id=item_id):
                unit = load_learning_unit(PATH_ID, item_id, project_root=self.root)
                self.assertEqual(unit.previous_item_id, previous)
                self.assertEqual(unit.next_item_id, following)

    def test_unknown_path_and_malformed_manifest_fail_closed_for_directory(self) -> None:
        with self.assertRaises(LearningUnitExperienceError) as caught:
            load_learning_path_directory("unknown-path", project_root=self.root)
        self.assertEqual(caught.exception.category, "unknown_learning_path")

        path = self.root / MANIFEST_RELATIVE
        original_text = path.read_text(encoding="utf-8")
        original = json.loads(original_text)
        malformed = json.loads(json.dumps(original))
        malformed["items"][1]["order"] = 1
        path.write_text(json.dumps(malformed), encoding="utf-8")
        with self.assertRaises(LearningUnitExperienceError) as caught:
            load_learning_path_directory(PATH_ID, project_root=self.root)
        self.assertEqual(caught.exception.category, "invalid_learning_path")

        path.write_text("{ malformed", encoding="utf-8")
        with self.assertRaises(LearningUnitExperienceError) as caught:
            load_learning_path_directory(PATH_ID, project_root=self.root)
        self.assertEqual(caught.exception.category, "invalid_learning_path")

        duplicate_key = original_text.replace(
            '"version": "1.0.0",', '"version": "1.0.0", "version": "2.0.0",', 1
        )
        path.write_text(duplicate_key, encoding="utf-8")
        with self.assertRaises(LearningUnitExperienceError) as caught:
            load_learning_path_directory(PATH_ID, project_root=self.root)
        self.assertEqual(caught.exception.category, "invalid_learning_path")

    def test_read_models_contain_no_progress_or_completion_facts(self) -> None:
        unit = load_learning_unit(PATH_ID, "checkin-001", project_root=self.root)
        directory = load_learning_path_directory(PATH_ID, project_root=self.root)
        for model in (asdict(unit), asdict(directory)):
            for forbidden in ("progress", "completed", "mastery", "review_due", "completion", "study_session"):
                self.assertNotIn(forbidden, model)

    def test_symlinked_content_directory_cannot_redirect_the_allowlisted_path(self) -> None:
        content = self.root / CONTENT_RELATIVE
        outside = self.root / "redirected-content"
        outside.mkdir()
        shutil.copyfile(content / "checkin-001.md", outside / "checkin-001.md")
        shutil.rmtree(content)
        content.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(LearningUnitExperienceError):
            load_learning_unit(PATH_ID, "checkin-001", project_root=self.root)

    def test_symlinked_markdown_cannot_escape_the_allowlisted_content_directory(self) -> None:
        content = self.root / CONTENT_RELATIVE
        path = content / "checkin-001.md"
        outside = self.root / "outside.md"
        outside.write_text("---\npath_id: system-architect-checkin\n---\n# outside", encoding="utf-8")
        path.unlink()
        path.symlink_to(outside)
        with self.assertRaises(LearningUnitExperienceError):
            load_learning_unit(PATH_ID, "checkin-001", project_root=self.root)


if __name__ == "__main__":
    unittest.main()
