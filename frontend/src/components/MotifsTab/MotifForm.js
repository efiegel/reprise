import React, { useState } from "react";
import {
  Box,
  TextField,
  Button,
  MenuItem,
  Select,
  InputLabel,
  FormControl,
  Switch,
} from "@mui/material";
import { motifService } from "../../services/motifService";

export default function MotifForm({ citations, onMotifAdded }) {
  const [newMotifContent, setNewMotifContent] = useState("");
  const [selectedCitation, setSelectedCitation] = useState("");
  const [autoGenerateClozeDeletions, setAutoGenerateClozeDeletions] =
    useState(true);

  const handleAddMotif = () => {
    if (!newMotifContent.trim()) return;

    motifService
      .createMotif(
        newMotifContent,
        selectedCitation,
        autoGenerateClozeDeletions
      )
      .then((data) => {
        onMotifAdded(data);
        setNewMotifContent("");
      })
      .catch((error) => {
        console.error("Error adding motif:", error);
      });
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      handleAddMotif();
    }
  };

  return (
    <Box mb={3}>
      <TextField
        fullWidth
        multiline
        minRows={3}
        label="New Motif Content"
        value={newMotifContent}
        onChange={(e) => setNewMotifContent(e.target.value)}
        onKeyDown={handleKeyDown}
        sx={{ mb: 2 }}
      />
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel id="citation-select-label" shrink={true}>
          Citation
        </InputLabel>
        <Select
          labelId="citation-select-label"
          value={selectedCitation}
          onChange={(e) => setSelectedCitation(e.target.value)}
          displayEmpty
        >
          <MenuItem value="">
            <em>None</em>
          </MenuItem>
          {citations.map((citation) => (
            <MenuItem key={citation.uuid} value={citation.title}>
              {citation.title}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}>
        <Button variant="contained" color="primary" onClick={handleAddMotif}>
          Add Motif
        </Button>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <Switch
            checked={autoGenerateClozeDeletions}
            onChange={(e) => setAutoGenerateClozeDeletions(e.target.checked)}
            color="primary"
          />
          <span style={{ color: "gray" }}>Auto-generate cloze deletions</span>
        </Box>
      </Box>
    </Box>
  );
}
