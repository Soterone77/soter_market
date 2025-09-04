import pytest

from app.categories.dao import CategoriesDAO


@pytest.mark.parametrize(
    "category_id,is_present",
    [
        (1, True),
        (3, True),
        (7, False),
    ],
)
async def test_find_user_by_id(category_id, is_present):
    category = await CategoriesDAO.find_one_or_none(id=category_id)

    if is_present:
        assert category
        assert category["id"] == category_id
    else:
        assert not category
