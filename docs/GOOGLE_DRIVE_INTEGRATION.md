# Google Drive Integration for Notes

This feature allows users to share Google Drive documents with their notes, enabling collaborative document sharing within the homework management system.

## Features Implemented

### Backend Integration
1. **Google Drive Service (`app/services/google_drive.py`):**
   - Extract file IDs from various Google Drive URL formats
   - Verify user access to shared files
   - Retrieve file metadata (name, MIME type, view link)
   - Make files publicly shareable when notes are public

2. **Database Schema Updates:**
   - Added Google Drive fields to the Note model:
     - `google_drive_file_id`: The unique Google Drive file identifier
     - `google_drive_file_url`: Direct link to view the file
     - `google_drive_file_name`: Display name for the file
     - `google_drive_mime_type`: File type information

3. **API Endpoints:**
   - `POST /api/notes/google-drive/attach`: Attach a Google Drive file to a note
   - `DELETE /api/notes/{note_id}/google-drive`: Remove Google Drive file from a note
   - `GET /api/notes/google-drive/file-info/{file_id}`: Get file information
   - Enhanced note creation/update to process Google Drive URLs automatically

### Frontend Integration
1. **Enhanced Note Creation/Editing:**
   - Added Google Drive URL input field in note modal
   - Optional custom file name field
   - Content field now serves as description for shared documents

2. **Note Display:**
   - Shows attached Google Drive files with file icons
   - Displays file name and type
   - Direct links to open files in Google Drive
   - Detach functionality for owned notes

3. **UI Components:**
   - Google Drive file info cards with proper styling
   - Attach/detach buttons with loading states
   - Error handling and user feedback

## How It Works

### URL Support
The system supports multiple Google Drive URL formats:
- `https://drive.google.com/file/d/FILE_ID/view`
- `https://drive.google.com/open?id=FILE_ID`
- `https://docs.google.com/document/d/FILE_ID/edit`
- `https://sheets.google.com/spreadsheets/d/FILE_ID/edit`
- Direct file IDs: `FILE_ID`

### Note Content as Description
When a Google Drive file is attached, the note's content field serves as a description of the shared document, making it easy to understand what the document contains without opening it.

### Public Sharing
When a note with an attached Google Drive file is made public:
1. The system attempts to make the Google Drive file publicly viewable
2. Other users can access both the note description and the shared document
3. Privacy is maintained for private notes

### User Workflow
1. **Create/Edit Note**: User enters note title and description
2. **Attach Drive File**: Paste any Google Drive URL or file ID
3. **Share**: Make note public to share both description and document
4. **Collaborate**: Other users can view the note and access the shared document

## Security & Privacy
- Users can only attach files they have access to in Google Drive
- File access verification happens on the backend
- Public notes only share files that can be made publicly accessible
- No unauthorized access to private Google Drive files

## Example Use Cases
1. **Study Materials**: Share lecture notes with document attachments
2. **Project Collaboration**: Link project documents with progress descriptions
3. **Resource Sharing**: Share educational resources with contextual descriptions
4. **Assignment Templates**: Provide assignment templates with instructions

This implementation provides seamless integration between the homework management system and Google Drive, enabling rich document sharing while maintaining security and user privacy.