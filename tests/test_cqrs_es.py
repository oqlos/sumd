"""Tests for CQRS ES architecture."""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from sumd.cqrs.events import (
    Event,
    EventStore,
    SumdDocumentCreated,
    SumdDocumentUpdated,
    SumdSectionAdded,
    SumdSectionRemoved,
    SumdDocumentValidated,
)
from sumd.cqrs.commands import (
    CommandBus,
    SumdCommandHandler,
    CreateSumdDocument,
    AddSumdSection,
    ValidateSumdDocument,
)
from sumd.cqrs.queries import (
    QueryBus,
    SumdQueryHandler,
    GetSumdDocument,
    GetEventHistory,
)
from sumd.cqrs.aggregates import EventSourcedRepository
from sumd.cqrs.sumd_aggregate import SumdAggregate


class TestEventStore:
    """Test EventStore functionality."""
    
    def test_save_and_get_events(self):
        """Test saving and retrieving events."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            storage_path = Path(tmp_dir)
            event_store = EventStore(storage_path)
            
            # Create test event
            event = SumdDocumentCreated(
                aggregate_id="test-aggregate",
                version=1,
                data={"project_name": "Test Project"},
            )
            
            # Save event
            event_store.save_event(event)
            
            # Retrieve events
            events = event_store.get_events("test-aggregate")
            assert len(events) == 1
            assert events[0].aggregate_id == "test-aggregate"
            assert events[0].data["project_name"] == "Test Project"
    
    def test_persistence(self):
        """Test event persistence to file."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            storage_path = Path(tmp_dir)
            
            # Create first event store and save event
            event_store1 = EventStore(storage_path)
            event = SumdDocumentCreated(
                aggregate_id="test-aggregate",
                version=1,
                data={"project_name": "Test Project"},
            )
            event_store1.save_event(event)
            
            # Create new event store instance and load events
            event_store2 = EventStore(storage_path)
            events = event_store2.get_events("test-aggregate")
            
            assert len(events) == 1
            assert events[0].data["project_name"] == "Test Project"

    def test_aggregate_id_cannot_escape_storage_directory(self, tmp_path):
        storage_path = tmp_path / "events"
        event_store = EventStore(storage_path)
        event_store.save_event(
            SumdDocumentCreated(
                aggregate_id="../escaped",
                data={"project_name": "Test Project"},
            )
        )

        assert not (tmp_path / "escaped.jsonl").exists()
        persisted = list(storage_path.glob("*.jsonl"))
        assert len(persisted) == 1
        assert persisted[0].parent == storage_path

        reloaded = EventStore(storage_path)
        assert len(reloaded.get_events("../escaped")) == 1
    
    def test_get_events_from_version(self):
        """Test retrieving events from specific version."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            storage_path = Path(tmp_dir)
            event_store = EventStore(storage_path)
            
            # Save multiple events
            for i in range(1, 4):
                event = SumdDocumentCreated(
                    aggregate_id="test-aggregate",
                    version=i,
                    data={"version": i},
                )
                event_store.save_event(event)
            
            # Get events from version 2
            events = event_store.get_events("test-aggregate", from_version=1)
            assert len(events) == 3
            
            events = event_store.get_events("test-aggregate", from_version=2)
            assert len(events) == 2


class TestSumdAggregate:
    """Test SumdAggregate functionality."""
    
    def test_create_document(self):
        """Test creating a SUMD document."""
        aggregate = SumdAggregate("test-aggregate")
        
        aggregate.create_document(
            project_name="Test Project",
            description="Test Description",
            file_path="/test/SUMD.md",
            profile="rich",
        )
        
        # Check state
        assert aggregate.state.project_name == "Test Project"
        assert aggregate.state.description == "Test Description"
        assert aggregate.state.file_path == "/test/SUMD.md"
        assert aggregate.state.profile == "rich"
        assert aggregate.state.created_at is not None
        assert aggregate.version == 1
        
        # Check uncommitted events
        events = aggregate.uncommitted_events
        assert len(events) == 1
        assert isinstance(events[0], SumdDocumentCreated)
    
    def test_add_section(self):
        """Test adding a section to document."""
        aggregate = SumdAggregate("test-aggregate")
        
        # Create document first
        aggregate.create_document("Test Project", "Test Description", "/test/SUMD.md")
        aggregate.mark_events_as_committed()
        
        # Add section
        aggregate.add_section(
            section_name="Architecture",
            section_type="architecture",
            content="Architecture content",
            level=2,
        )
        
        # Check state
        assert len(aggregate.state.sections) == 1
        section = aggregate.state.sections[0]
        assert section.name == "Architecture"
        assert section.section_type == "architecture"
        assert section.content == "Architecture content"
        assert aggregate.version == 2
    
    def test_remove_section(self):
        """Test removing a section from document."""
        aggregate = SumdAggregate("test-aggregate")
        
        # Create document and add section
        aggregate.create_document("Test Project", "Test Description", "/test/SUMD.md")
        aggregate.mark_events_as_committed()
        aggregate.add_section("Architecture", "architecture", "Content")
        aggregate.mark_events_as_committed()
        
        # Remove section
        aggregate.remove_section("Architecture")
        
        # Check state
        assert len(aggregate.state.sections) == 0
        assert aggregate.version == 3
    
    def test_load_from_history(self):
        """Test loading aggregate from event history."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            storage_path = Path(tmp_dir)
            event_store = EventStore(storage_path)
            
            # Create events
            events = [
                SumdDocumentCreated(
                    aggregate_id="test-aggregate",
                    version=1,
                    data={"project_name": "Test Project", "description": "Test Description", "file_path": "/test/SUMD.md"},
                ),
                SumdSectionAdded(
                    aggregate_id="test-aggregate",
                    version=2,
                    data={"section_name": "Architecture", "section_type": "architecture", "content": "Content"},
                ),
            ]
            
            # Save events
            for event in events:
                event_store.save_event(event)
            
            # Load aggregate from history
            aggregate = SumdAggregate("test-aggregate")
            aggregate.set_event_store(event_store)
            history_events = event_store.get_events("test-aggregate")
            aggregate.load_from_history(history_events)
            
            # Check state
            assert aggregate.state.project_name == "Test Project"
            assert len(aggregate.state.sections) == 1
            assert aggregate.version == 2


class TestCommandBus:
    """Test CommandBus functionality."""
    
    @pytest.mark.asyncio
    async def test_dispatch_command(self):
        """Test dispatching commands."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            storage_path = Path(tmp_dir)
            event_store = EventStore(storage_path)
            command_bus = CommandBus(event_store)
            command_handler = SumdCommandHandler(event_store)
            
            # Register handler
            command_bus.register_handler("create_sumd_document", command_handler)
            
            # Create command
            command = CreateSumdDocument(
                aggregate_id="test-aggregate",
                data={
                    "project_name": "Test Project",
                    "description": "Test Description",
                    "file_path": "/test/SUMD.md",
                },
            )
            
            # Dispatch command
            events = await command_bus.dispatch(command)
            
            # Check results
            assert len(events) == 2  # DocumentCreated + CommandExecuted
            assert events[0].event_type == "sumd_document_created"
            assert events[1].event_type == "sumd_command_executed"
            
            # Check event storage
            stored_events = event_store.get_events("test-aggregate")
            assert len(stored_events) == 2


class TestQueryBus:
    """Test QueryBus functionality."""
    
    @pytest.mark.asyncio
    async def test_dispatch_query(self):
        """Test dispatching queries."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create test SUMD file
            test_file = Path(tmp_dir) / "SUMD.md"
            test_file.write_text("""# Test Project

## Intent
Test description

## Architecture
Test architecture
""")
            
            storage_path = Path(tmp_dir) / "events"
            event_store = EventStore(storage_path)
            query_bus = QueryBus(event_store)
            query_handler = SumdQueryHandler(event_store)
            
            # Register handler
            query_bus.register_handler("get_sumd_document", query_handler)
            
            # Create query
            query = GetSumdDocument(parameters={"file_path": str(test_file)})
            
            # Dispatch query
            result = await query_bus.dispatch(query)
            
            # Check results
            assert result["success"] is True
            assert result["data"]["project_name"] == "Test Project"
            assert len(result["data"]["sections"]) == 2


class TestEventSourcedRepository:
    """Test EventSourcedRepository functionality."""
    
    @pytest.mark.asyncio
    async def test_save_and_get_aggregate(self):
        """Test saving and retrieving aggregates."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            storage_path = Path(tmp_dir)
            event_store = EventStore(storage_path)
            repository = EventSourcedRepository(event_store, SumdAggregate)
            
            # Create aggregate
            aggregate = SumdAggregate("test-aggregate")
            aggregate.create_document("Test Project", "Test Description", "/test/SUMD.md")
            
            # Save aggregate
            await repository.save(aggregate)
            
            # Retrieve aggregate
            retrieved = await repository.get_by_id("test-aggregate")
            
            # Check results
            assert retrieved is not None
            assert retrieved.aggregate_id == "test-aggregate"
            assert retrieved.state.project_name == "Test Project"
            assert retrieved.version == 1


class TestIntegration:
    """Integration tests for CQRS ES architecture."""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test complete CQRS ES workflow."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create test SUMD file
            test_file = Path(tmp_dir) / "SUMD.md"
            test_file.write_text("""# Test Project

## Intent
Test description
""")
            
            storage_path = Path(tmp_dir) / "events"
            event_store = EventStore(storage_path)
            
            # Setup CQRS components
            command_bus = CommandBus(event_store)
            query_bus = QueryBus(event_store)
            command_handler = SumdCommandHandler(event_store)
            query_handler = SumdQueryHandler(event_store)
            repository = EventSourcedRepository(event_store, SumdAggregate)
            
            # Register handlers
            command_bus.register_handler("create_sumd_document", command_handler)
            command_bus.register_handler("add_sumd_section", command_handler)
            query_bus.register_handler("get_sumd_document", query_handler)
            query_bus.register_handler("get_event_history", query_handler)
            
            # Execute workflow
            aggregate_id = str(test_file)
            
            # 1. Create document
            create_cmd = CreateSumdDocument(
                aggregate_id=aggregate_id,
                data={
                    "project_name": "Test Project",
                    "description": "Test Description",
                    "file_path": str(test_file),
                },
            )
            events1 = await command_bus.dispatch(create_cmd)
            assert len(events1) == 2
            
            # 2. Add section
            add_section_cmd = AddSumdSection(
                aggregate_id=aggregate_id,
                data={
                    "section_name": "Architecture",
                    "section_type": "architecture",
                    "content": "Architecture content",
                },
            )
            events2 = await command_bus.dispatch(add_section_cmd)
            assert len(events2) == 2
            
            # 3. Query document
            query = GetSumdDocument(parameters={"file_path": str(test_file)})
            result = await query_bus.dispatch(query)
            assert result["success"] is True
            
            # 4. Get event history
            history_query = GetEventHistory(parameters={"aggregate_id": aggregate_id})
            history = await query_bus.dispatch(history_query)
            assert history["success"] is True
            assert len(history["data"]) == 4  # 2 commands * 2 events each
            
            # 5. Verify aggregate state
            aggregate = await repository.get_by_id(aggregate_id)
            assert aggregate is not None
            assert aggregate.state.project_name == "Test Project"
            assert len(aggregate.state.sections) >= 1  # Original sections + added section


if __name__ == "__main__":
    pytest.main([__file__])
