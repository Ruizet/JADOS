# memory/page_replacement.py

class PageReplacementSimulator:
    def __init__(self):
        pass

    def parse_reference_string(self, ref_str: str) -> list:
        try:
            return [int(x.strip()) for x in ref_str.split() if x.strip().isdigit()]
        except:
            return []

    def simulate(self, algorithm: str, ref_string: str, num_frames: int, clean_time: int = 3) -> dict:
        refs = self.parse_reference_string(ref_string)
        if not refs or num_frames <= 0:
            return None

        if algorithm == "FIFO": return self._sim_fifo(refs, num_frames)
        elif algorithm == "LRU": return self._sim_lru(refs, num_frames)
        elif algorithm == "OPT": return self._sim_opt(refs, num_frames)
        elif algorithm == "NRU": return self._sim_nru(refs, num_frames, clean_time)
        return None

    def _format_result(self, algorithm: str, steps: list, faults: int, total_refs: int, msg: str = "Simulación completada con éxito.") -> dict:
        rate = (faults / total_refs) * 100 if total_refs > 0 else 0
        return {
            "algorithm": algorithm,
            "steps": steps,
            "total_faults": faults,
            "fault_rate": rate,
            "message": msg
        }

    def _build_frames_list(self, current_frames: list, num_frames: int) -> list:
        return [current_frames[i] if i < len(current_frames) else "" for i in range(num_frames)]

    def _sim_fifo(self, refs: list, num_frames: int) -> dict:
        frames, queue, faults, steps = [], [], 0, []
        for i, page in enumerate(refs):
            is_fault = False
            if page not in frames:
                is_fault = True
                faults += 1
                if len(frames) < num_frames:
                    frames.append(page)
                    queue.append(page)
                else:
                    idx = frames.index(queue.pop(0))
                    frames[idx] = page
                    queue.append(page)
            steps.append({"step": i+1, "page": page, "frames": self._build_frames_list(frames, num_frames), "is_fault": is_fault, "status_mark": "F" if is_fault else "OK"})
        return self._format_result("FIFO", steps, faults, len(refs))

    def _sim_lru(self, refs: list, num_frames: int) -> dict:
        frames, last_used, faults, steps = [], {}, 0, []
        for i, page in enumerate(refs):
            is_fault = False
            if page not in frames:
                is_fault = True
                faults += 1
                if len(frames) < num_frames: frames.append(page)
                else:
                    idx = frames.index(min(frames, key=lambda p: last_used.get(p, -1)))
                    frames[idx] = page
            last_used[page] = i
            steps.append({"step": i+1, "page": page, "frames": self._build_frames_list(frames, num_frames), "is_fault": is_fault, "status_mark": "F" if is_fault else "OK"})
        return self._format_result("LRU", steps, faults, len(refs))

    def _sim_opt(self, refs: list, num_frames: int) -> dict:
        frames, faults, steps = [], 0, []
        for i, page in enumerate(refs):
            is_fault = False
            if page not in frames:
                is_fault = True
                faults += 1
                if len(frames) < num_frames: frames.append(page)
                else:
                    farthest, victim = -1, -1
                    for p in frames:
                        try: next_use = refs.index(p, i + 1)
                        except ValueError: next_use = float('inf')
                        if next_use > farthest: farthest, victim = next_use, p
                    frames[frames.index(victim)] = page
            steps.append({"step": i+1, "page": page, "frames": self._build_frames_list(frames, num_frames), "is_fault": is_fault, "status_mark": "F" if is_fault else "OK"})
        return self._format_result("OPT", steps, faults, len(refs))

    def _sim_nru(self, refs: list, num_frames: int, clean_time: int) -> dict:
        frames = [] 
        faults = 0
        steps = []

        for i, page in enumerate(refs):
            step_num = i + 1
            is_clean_event = (step_num % clean_time == 0)

            if is_clean_event:
                for f in frames:
                    f["R"] = 0

            is_fault = False
            page_idx = next((idx for idx, f in enumerate(frames) if f["page"] == page), -1)

            if page_idx != -1:
                frames[page_idx]["R"] = 1
                frames[page_idx]["M"] = 1 
            else:
                is_fault = True
                faults += 1
                if len(frames) < num_frames:
                    frames.append({"page": page, "R": 1, "M": 0})
                else:
                    classes = {0: [], 1: [], 2: [], 3: []}
                    for idx, f in enumerate(frames):
                        clase = (f["R"] * 2) + f["M"]
                        classes[clase].append(idx)
                        
                    victim_idx = -1
                    for c in range(4):
                        if classes[c]:
                            victim_idx = classes[c][0] 
                            break
                    frames[victim_idx] = {"page": page, "R": 1, "M": 0}

            # En lugar de un string, devolvemos un diccionario estructurado para cada marco
            visual_frames = []
            for r in range(num_frames):
                if r < len(frames):
                    visual_frames.append({"val": frames[r]["page"], "R": frames[r]["R"], "M": frames[r]["M"]})
                else:
                    visual_frames.append({"val": "", "R": "", "M": ""})
            
            steps.append({
                "step": step_num,
                "page": page,
                "frames": visual_frames,
                "is_fault": is_fault,
                "status_mark": "F" if is_fault else "OK",
                "is_clean": is_clean_event 
            })

        return self._format_result("NRU", steps, faults, len(refs))