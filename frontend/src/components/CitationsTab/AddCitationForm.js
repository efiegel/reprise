import React, { useState } from "react";
import { Box, TextField, Button } from "@mui/material";

export const AddCitationForm = ({ onAddCitation }) => {
  const [title, setTitle] = useState("");

  const handleSubmit = async () => {
    if (!title.trim()) return;

    const citation = await onAddCitation(title);
    if (citation) {
      setTitle("");
    }
  };

  return (
    <Box mb={3}>
      <TextField
        fullWidth
        label="New Citation Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        sx={{ mb: 2 }}
      />
      <Button variant="contained" color="primary" onClick={handleSubmit}>
        Add Citation
      </Button>
    </Box>
  );
};
