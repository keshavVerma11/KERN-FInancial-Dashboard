"""
SQLAlchemy database models
"""
from sqlalchemy import Column, String, Float, Date, Boolean, DateTime, ForeignKey, Text, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import uuid
import enum


class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    CLIENT = "client"


class DocumentStatus(str, enum.Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TransactionStatus(str, enum.Enum):
    """Transaction review status"""
    PENDING = "pending"
    REVIEWED = "reviewed"
    FLAGGED = "flagged"


class Organization(Base):
    """
    Organizations/Companies table
    Each client company is an organization
    """
    __tablename__ = "organizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="organization")
    transactions = relationship("Transaction", back_populates="organization")
    documents = relationship("Document", back_populates="organization")


class User(Base):
    """
    Users table (synced with Supabase Auth)
    """
    __tablename__ = "users"
    
    # Use same ID as Supabase auth.users
    id = Column(UUID(as_uuid=True), primary_key=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.CLIENT)
    full_name = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="users")


class Document(Base):
    """
    Uploaded financial documents
    """
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50))  # pdf, csv, xlsx, etc.
    file_size = Column(Integer)  # in bytes
    storage_path = Column(String(500))  # S3 or Supabase storage path
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.PENDING)
    error_message = Column(Text)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    
    # Relationships
    organization = relationship("Organization", back_populates="documents")
    transactions = relationship("Transaction", back_populates="source_document")


class Category(Base):
    """
    Chart of Accounts categories
    """
    __tablename__ = "categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)  # NULL = global category
    code = Column(String(50))  # e.g., "4000" for revenue
    name = Column(String(255), nullable=False)  # e.g., "Sales Revenue"
    type = Column(String(50))  # revenue, expense, asset, liability, equity
    parent_category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))  # for subcategories
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    transactions = relationship("Transaction", back_populates="category")
    parent = relationship("Category", remote_side=[id])


class Transaction(Base):
    """
    Financial transactions
    """
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    source_document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    
    # Transaction details
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(500))
    merchant = Column(String(255))
    
    # Categorization
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    confidence_score = Column(Float)  # AI classification confidence (0-1)
    
    # Status and review
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_at = Column(DateTime(timezone=True))
    
    # Metadata
    notes = Column(Text)
    tags = Column(String(500))  # Comma-separated tags
    is_transfer = Column(Boolean, default=False)  # Internal transfer (not expense/income)
    is_owner_draw = Column(Boolean, default=False)
    payment_method = Column(String(50))  # cash, card, ach, check
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="transactions")
    source_document = relationship("Document", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")


class ClassificationHistory(Base):
    """
    History of AI classifications for learning
    """
    __tablename__ = "classification_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"))
    
    # AI suggestion
    suggested_category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    confidence_score = Column(Float)
    rationale = Column(Text)  # AI's reasoning
    
    # Human override
    was_accepted = Column(Boolean)
    actual_category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
