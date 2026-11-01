from sqlalchemy import Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class DimGender(Base):
    __tablename__ = "dim_gender"

    gender_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    gender_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    __table_args__ = (
        CheckConstraint("gender_name IN ('Male', 'Female', 'Other', 'Non-binary')", name="chk_gender_name"),
    )


class DimAcademic(Base):
    __tablename__ = "dim_academic"

    academic_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    academic_level: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    tier_level: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("academic_level IN ('High School', 'Undergraduate', 'Graduate')", name="chk_academic_level"),
        CheckConstraint("tier_level BETWEEN 1 AND 3", name="chk_academic_tier"),
    )


class DimCountry(Base):
    __tablename__ = "dim_country"

    country_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    country_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    region: Mapped[str] = mapped_column(String(50), default="Global", nullable=False)


class DimPlatform(Base):
    __tablename__ = "dim_platform"

    platform_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    platform_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    platform_category: Mapped[str] = mapped_column(String(50), default="Social", nullable=False)

    __table_args__ = (
        CheckConstraint(
            "platform_category IN ('Social', 'Messaging', 'Video', 'Professional', 'Other')",
            name="chk_platform_category"
        ),
    )


class DimPurpose(Base):
    __tablename__ = "dim_purpose"

    purpose_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    purpose_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "purpose_name IN ('Education', 'Entertainment', 'Networking', 'News', 'Other')",
            name="chk_purpose_name"
        ),
    )


class DimStress(Base):
    __tablename__ = "dim_stress"

    stress_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stress_level: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    stress_rank: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("stress_level IN ('Low', 'Medium', 'High', 'Very High')", name="chk_stress_level"),
        CheckConstraint("stress_rank BETWEEN 1 AND 4", name="chk_stress_rank"),
    )


class DimRespondent(Base):
    __tablename__ = "dim_respondent"

    respondent_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_respondent_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_gender.gender_key"), nullable=False)
    academic_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_academic.academic_key"), nullable=False)

    gender: Mapped["DimGender"] = relationship("DimGender")
    academic: Mapped["DimAcademic"] = relationship("DimAcademic")

    __table_args__ = (
        CheckConstraint("age BETWEEN 10 AND 100", name="chk_respondent_age"),
    )

