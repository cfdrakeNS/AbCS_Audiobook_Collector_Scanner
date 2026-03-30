# Web Search Changes - Author and Title Handling

## Overview
Plan to address web search considerations for author and title in web_metadata system.

## Preference Settings Found

### Author Flipping
- **Setting**: `flip_author_name` 
- **Location**: Preferences → Options → "Flip Author Name Last, First"
- **Default**: False
- **Setting Key**: `import/flip_author_name`
- **Purpose**: User preference for author name format

### Title Article Movement  
- **Setting**: `autocorrect_move_the_check`
- **Location**: Preferences → Options → "Move leading 'The', 'A', 'An' to end of title"
- **Default**: False
- **Setting Key**: `import/autocorrect/move_leading_the_title`
- **Purpose**: User preference for title article format
- **Articles Handled**: "The", "A", "An" (moved to end as ", The", ", A", ", An")

## Important Note
The web metadata system must examine the **actual title and author stored in the database**, not rely on import history. Books may have been added manually or through different methods. User preferences only come into play when storing/updating data, not during the initial web search.

## 2 Items to Address in web_metadata

### 1. Search
**Issue**: Web search needs to handle series numbers in titles for better matching

**Current Behavior**: 
- Web search uses title/author as-is from database
- May not find matches if series numbers are included

**Required Changes**:
- Examine the **actual title and author stored in database**
- Strip series numbers before searching to improve match chances:
  - "The Moon - 09" → Search for "The Moon"
  - "09 The Moon" → Search for "The Moon" 
  - "2001: A Space Odyssey" → Search as-is (real numeric title, not series)

**Implementation**:
- Read current title/author from database
- Strip series numbers (patterns like " - ##", "## ", etc.)
- Search with clean title for better web matches
- Return best match found

### 2. Handling Preference Settings When Adding Data to DB
**Issue**: When web metadata is applied, need to respect user formatting preferences and clean data

**Current Behavior**:
- Web metadata stores data exactly as received from web service
- No consideration for user preferences or data cleaning

**Required Changes**:
- Apply user preferences and clean data before storing web metadata:
  - If author flip enabled: "John Smith" → "Smith, John"
  - If title article move enabled: "The Moon" → "Moon, The", "A Tale" → "Tale, A", "An Adventure" → "Adventure, An"
  - Handle series numbers correctly: "The Moon - 09" → "Moon, The - 09", "A Story - 03" → "Story, A - 03"

**Implementation**:
- Read user preferences from settings
- Strip existing series numbers before applying transformations
- Apply transformations to base title, then re-add series number
- Maintain data integrity and avoid double-formatting

## web_metadata Adding to DB

Since we don't have a way of reviewing books like import, we should always clean the data when adding web metadata to the database.

### Title, Author Cleaning:
- Converts multiple spaces to single spaces and trims ends
- Removes non-alphanumeric characters from start
- Capitalizes first letter of each word
- Remove special characters
- Follow preferences for Flip author and Moving "The", "A", "An" to end of title

### Series, Genre, Plot Cleaning:
- Converts multiple spaces to single spaces and trims ends
- Removes non-alphanumeric characters from start
- Remove special characters

## Implementation Plan

### Phase 1: Search Enhancement
1. **Modify Web Search Functions**
   - Add preference-aware search variations
   - Try both original and transformed search terms
   - Return best match across all attempts

2. **Search Strategy**
   - Primary search: Original title/author
   - Secondary search: Preference-transformed versions
   - Merge and rank results

### Phase 2: Data Storage Enhancement  
1. **Apply Preferences Before Storage**
   - Read user preference settings
   - Transform web metadata according to preferences
   - Store formatted data in database

2. **Handle Series Numbers**
   - Apply title article move BEFORE adding series number
   - Example: "The Moon" → "Moon, The" → "Moon, The - 09"

### Phase 3: Testing
1. **Search Tests**
   - Test web search finds matches with both formats
   - Test preference variations improve search success

2. **Storage Tests**  
   - Test preferences are applied correctly before storage
   - Test series number handling with article movement

## Success Criteria
1. Web search finds more matches by trying preference variations
2. Stored web metadata respects user formatting preferences
3. Series numbers handled correctly with title article movement
