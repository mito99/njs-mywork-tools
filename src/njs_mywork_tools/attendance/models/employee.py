import re
from dataclasses import dataclass


@dataclass
class Employee:
    """
    従業員の姓名を保持するデータクラス
    """

    given_name: str
    family_name: str

    def full_name(self) -> str:
        """
        氏名を結合して返す
        Returns:
            str: 氏名
        """
        return f"{self.last_name} {self.first_name}"

    @classmethod
    def from_full_name(cls, full_name: str) -> "Employee":
        """
        スペース区切りの氏名文字列からEmployeeオブジェクトを生成する
        Args:
            full_name: スペース区切りの氏名文字列
        Returns:
            Employee: Employeeオブジェクト
        Raises:
            ValueError: 氏名が姓と名の2つに分割できない場合
        """
        names = re.split(r"\s+", full_name.strip())
        if len(names) != 2:
            raise ValueError(f"氏名が姓と名の2つに分割できません: {full_name}")
        return cls(family_name=names[0], given_name=names[1])
