# Replacement code for BookListImportWindow (collection combo and logic)
# For use between ###START replace code and ###@END replace code markers in book_list_import_window.py

# --- OPTIONS SECTION (setup_ui) ---
# Place this immediately after the file selection group and before the rest of the options section.

# Collection selection group
collection_group = QGroupBox("Collection")
collection_group.setAccessibleName("Collection group")
collection_layout = QHBoxLayout(collection_group)

collection_label = QLabel("&Collection:")
self.collection_combo = QComboBox()
self.collection_combo.setAccessibleName("Import collection")
self.collection_combo.setAccessibleDescription(
    "Select target collection for imported books - Alt+C"
)
collection_label.setBuddy(self.collection_combo)
collection_layout.addWidget(collection_label)
collection_layout.addWidget(self.collection_combo, 1)
collection_group.setLayout(collection_layout)

main_layout.addWidget(collection_group)

# Populate collections
self._load_collection_options()

# --- END OPTIONS SECTION ---

# --- INITIALIZATION AND LOGIC (in __init__ and helpers) ---
def _load_collection_options(self):
    """Load target collection options for imports."""
    self.collection_combo.blockSignals(True)
    self.collection_combo.clear()

    collections = self.collection_queries.get_all(active_only=True)
    if not collections:
        default_collection = Collection(name="Default", active=True)
        new_id = self.collection_queries.insert(default_collection)
        collections = [
            Collection(collection_id=new_id, name="Default", active=True)
        ]

    collections = sorted(
        collections,
        key=lambda collection: (collection.name or "").casefold(),
    )

    for collection in collections:
        self.collection_combo.addItem(collection.name, collection.collection_id)

    # Selection logic: match main window logic
    if hasattr(self, "main_collection_id") and self.main_collection_id is not None:
        idx = self.collection_combo.findData(self.main_collection_id)
        if idx >= 0:
            self.collection_combo.setCurrentIndex(idx)
        else:
            self.collection_combo.setCurrentIndex(-1)
    elif len(collections) == 1:
        self.collection_combo.setCurrentIndex(0)
    elif len(collections) > 1:
        self.collection_combo.setCurrentIndex(-1)  # No selection
    else:
        self.collection_combo.setCurrentIndex(-1)

    self.collection_combo.blockSignals(False)

# --- END INITIALIZATION AND LOGIC ---

# In main_window.py, when launching BookListImportWindow, pass main_collection_id as:
# dialog = BookListImportWindow(self.db, self.scaler, self.theme_manager, parent=self, main_collection_id=self.current_filter.collection_id)

