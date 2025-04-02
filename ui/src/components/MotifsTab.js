import React, { useState, useEffect } from "react";
import {
  Box,
  CircularProgress,
  Pagination,
  FormControlLabel,
  Switch,
} from "@mui/material";
import { useMotifs } from "../hooks/useMotifs";
import { motifService } from "../services/motifService";
import MotifForm from "./MotifsTab/MotifForm";
import MotifTable from "./MotifsTab/MotifTable";
import ClozeDeletionModal from "./MotifsTab/ClozeDeletionModal";

export default function MotifsTab() {
  // Pagination state
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);

  // UI state
  const [deleteEnabled, setDeleteEnabled] = useState(false);
  const [showClozeDeletions, setShowClozeDeletions] = useState(true);

  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMotif, setModalMotif] = useState(null);
  const [selectedBins, setSelectedBins] = useState(new Set());
  const [isDragging, setIsDragging] = useState(false);

  // Use custom hook for motif data management
  const {
    motifs,
    setMotifs,
    totalMotifs,
    citations,
    isLoading,
    hoveredClozeSet,
    setHoveredClozeSet,
    fetchMotifs,
  } = useMotifs(page, pageSize);

  useEffect(() => {
    fetchMotifs();
  }, [page, pageSize]);

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  const handleOpenModal = (
    motif,
    clozeDeletionSet,
    clozeDeletionUuid = null
  ) => {
    setModalMotif({ ...motif, clozeDeletionUuid });

    const initialBins = new Set(
      (clozeDeletionSet || []).flatMap(([start, end]) =>
        Array.from({ length: end - start + 1 }, (_, i) => start + i)
      )
    );

    setSelectedBins(initialBins);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setModalMotif(null);
  };

  const handleSaveTuples = () => {
    const mask_tuples = [];
    let start = null;

    [...selectedBins]
      .sort((a, b) => a - b)
      .forEach((index, i, arr) => {
        if (start === null) start = index;
        if (i === arr.length - 1 || arr[i + 1] !== index + 1) {
          mask_tuples.push([start, index]);
          start = null;
        }
      });

    motifService
      .saveClozeDeletion(
        modalMotif.uuid,
        mask_tuples,
        modalMotif.clozeDeletionUuid
      )
      .then((data) => {
        updateMotifsWithClozeDeletion(data, modalMotif);
      })
      .catch((error) => {
        console.error("Error saving cloze deletion:", error);
      });

    handleCloseModal();
  };

  const updateMotifsWithClozeDeletion = (data, modalMotif) => {
    setMotifs((prevMotifs) =>
      prevMotifs.map((motif) =>
        motif.uuid === modalMotif.uuid
          ? {
              ...motif,
              cloze_deletions: modalMotif.clozeDeletionUuid
                ? motif.cloze_deletions.map((cd) =>
                    cd.uuid === data.uuid ? data : cd
                  )
                : [...(motif.cloze_deletions || []), data],
            }
          : motif
      )
    );
  };

  const handleDeleteClozeDeletion = () => {
    if (!modalMotif.clozeDeletionUuid) return;

    motifService
      .deleteClozeDeletion(modalMotif.clozeDeletionUuid)
      .then(() => {
        setMotifs((prevMotifs) =>
          prevMotifs.map((motif) =>
            motif.uuid === modalMotif.uuid
              ? {
                  ...motif,
                  cloze_deletions: motif.cloze_deletions.filter(
                    (cd) => cd.uuid !== modalMotif.clozeDeletionUuid
                  ),
                }
              : motif
          )
        );
      })
      .catch((error) => {
        console.error("Error deleting cloze deletion:", error);
      });

    handleCloseModal();
  };

  // Bin selection handlers for the modal
  const handleMouseDown = (index) => {
    setIsDragging(true);
    setSelectedBins((prev) => {
      const newBins = new Set(prev);
      if (prev.has(index)) {
        newBins.delete(index);
      } else {
        newBins.add(index);
      }
      return newBins;
    });
  };

  const handleMouseEnter = (index) => {
    if (isDragging) {
      setSelectedBins((prev) => {
        const newBins = new Set(prev);
        if (prev.has(index)) {
          newBins.delete(index);
        } else {
          newBins.add(index);
        }
        return newBins;
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  return (
    <Box>
      <MotifForm
        citations={citations}
        onMotifAdded={(motif) => setMotifs([motif, ...motifs])}
      />

      {isLoading ? (
        <CircularProgress />
      ) : (
        <>
          <MotifTable
            motifs={motifs}
            deleteEnabled={deleteEnabled}
            showClozeDeletions={showClozeDeletions}
            hoveredClozeSet={hoveredClozeSet}
            setHoveredClozeSet={setHoveredClozeSet}
            onOpenModal={handleOpenModal}
            onMotifUpdate={(updatedMotif) => {
              setMotifs((prevMotifs) =>
                prevMotifs.map((m) =>
                  m.uuid === updatedMotif.uuid ? updatedMotif : m
                )
              );
            }}
            onMotifDelete={(uuid) => {
              setMotifs((prevMotifs) =>
                prevMotifs.filter((m) => m.uuid !== uuid)
              );
            }}
          />

          <Pagination
            count={Math.ceil(totalMotifs / pageSize)}
            page={page}
            onChange={handlePageChange}
            sx={{ mt: 2 }}
          />
        </>
      )}

      <Box mt={3}>
        <FormControlLabel
          control={
            <Switch
              checked={deleteEnabled}
              onChange={(e) => setDeleteEnabled(e.target.checked)}
              color="primary"
            />
          }
          label="Show delete buttons"
        />
      </Box>

      <Box mt={3}>
        <FormControlLabel
          control={
            <Switch
              checked={showClozeDeletions}
              onChange={() => setShowClozeDeletions((prev) => !prev)}
            />
          }
          label="Show cloze deletions"
          sx={{ mb: 2 }}
        />
      </Box>

      <ClozeDeletionModal
        open={isModalOpen}
        motif={modalMotif}
        selectedBins={selectedBins}
        onClose={handleCloseModal}
        onSave={handleSaveTuples}
        onDelete={handleDeleteClozeDeletion}
        onMouseDown={handleMouseDown}
        onMouseEnter={handleMouseEnter}
        onMouseUp={handleMouseUp}
      />
    </Box>
  );
}
