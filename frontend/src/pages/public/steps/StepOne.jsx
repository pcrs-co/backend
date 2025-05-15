// src/pages/public/steps/StepOne.jsx
import React from "react";

const StepOne = ({ data, updateData }) => {
  return (
    <div>
      <h2 className="text-xl font-bold mb-2">User Background</h2>

      <label>What is your profession or field of work/study?</label>
      <input
        type="text"
        className="block mb-4 border p-2"
        value={data.profession || ""}
        onChange={(e) => updateData({ profession: e.target.value })}
      />

      <label>What is your technical experience level?</label>
      <select
        className="block mb-4 border p-2"
        value={data.tech_level || ""}
        onChange={(e) => updateData({ tech_level: e.target.value })}
      >
        <option value="">-- Select --</option>
        <option>Beginner</option>
        <option>Intermediate</option>
        <option>Expert</option>
      </select>

      <label>How frequently do you use a computer?</label>
      <select
        className="block mb-4 border p-2"
        value={data.usage_freq || ""}
        onChange={(e) => updateData({ usage_freq: e.target.value })}
      >
        <option value="">-- Select --</option>
        <option>Occasionally</option>
        <option>Daily</option>
        <option>All-day use</option>
      </select>
    </div>
  );
};

export default StepOne;
