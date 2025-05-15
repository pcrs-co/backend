import React, { useState } from 'react';
import Button from '../../features/ReusableButton';

const InputBasic = () => {
  const [experienceLevel, setExperienceLevel] = useState('');
  const [formData, setFormData] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    const numericValue = value === "" ? "" : parseInt(value, 10);

    setFormData((prev) => {
      const updated = { ...prev, [name]: numericValue };

      // Validation: Budget range logic
      if (
        name === "budgetMin" &&
        updated.budgetMax &&
        numericValue > updated.budgetMax
      ) {
        toast.error("Minimum budget cannot exceed maximum budget");
      }

      if (
        name === "budgetMax" &&
        updated.budgetMin &&
        numericValue < updated.budgetMin
      ) {
        toast.error("Maximum budget cannot be less than minimum budget");
      }

      return updated;
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Submitted Data:', { experienceLevel, ...formData });
    // Add API integration or state management logic here
  };

  return (
    <>
      <div className="container mt-3">
        <Button to="/" variant="outline-primary" className="d-inline-flex align-items-center">
          Home
        </Button>
      </div>
      <div className="container mt-5 mb-3 d-flex flex-column align-items-center w-75">
        <h2 className="mb-4">Help Us Recommend you a Laptop</h2>
        <form onSubmit={handleSubmit} className="w-100">
          <div className="form-outline mb-4">
            <label className="form-label">What is your profession or field of work/study?</label>
            <input type="text" name="profession" className="form-control" onChange={handleChange} />
          </div>

          <div className="form-outline mb-4">
            <label className="form-label">What is your technical experience level?</label>
            <select name="experience" className="form-control" onChange={(e) => {
              setExperienceLevel(e.target.value);
              handleChange(e);
            }}>
              <option value="">Select</option>
              <option value="Beginner">Beginner</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Expert">Expert</option>
            </select>
          </div>

          <div className="form-outline mb-4">
            <label className="form-label">What do you primarily use a computer for?</label>
            <select name="activities" className="form-control" onChange={handleChange}>
              <option value="">Select</option>
              <option value="Office">Office & Productivity</option>
              <option value="Creative">Creative & Design Work</option>
              <option value="Development">Development & Technical Tasks</option>
            </select>
          </div>

          <div className="form-outline mb-4">
            <label className="form-label">List any specific applications or software you use regularly.</label>
            <input type="text" name="apps" className="form-control" onChange={handleChange} />
          </div>

          {experienceLevel === 'Expert' && (
            <>
              <div className="form-outline mb-4">
                <label className="form-label">Do you plan to use virtual machines or emulators?</label>
                <select name="vms" className="form-control" onChange={handleChange}>
                  <option value="">Select</option>
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>

              <div className="form-outline mb-4">
                <label className="form-label">Do you want a dedicated graphics card (GPU)?</label>
                <select name="gpu" className="form-control" onChange={handleChange}>
                  <option value="">Select</option>
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>

              <div className="form-outline mb-4">
                <label className="form-label">Minimum RAM requirement (GB)</label>
                <input type="number" name="ram" className="form-control" onChange={handleChange} />
              </div>

              <div className="form-outline mb-4">
                <label className="form-label">Preferred storage size (GB)</label>
                <input type="number" name="storage" className="form-control" onChange={handleChange} />
              </div>
            </>
          )}

          <div className="form-outline mb-4">
            <label className="form-label">How important is battery life to you?</label>
            <select name="battery" className="form-control" onChange={handleChange}>
              <option value="">Select</option>
              <option value="Not Important">Not Important</option>
              <option value="Somewhat Important">Somewhat Important</option>
              <option value="Very Important">Very Important</option>
            </select>
          </div>

          <div className="row mb-4">
            <div className="col">
              <label className="form-label" htmlFor="budgetMin">Budget Range (TShs)</label>
              <div className="input-group">
                <span className="input-group-text">Min</span>
                <input
                  type="number"
                  name="budgetMin"
                  id="budgetMin"
                  className="form-control"
                  placeholder="e.g. 500000"
                  onChange={handleChange}
                  min="0"
                />
              </div>
            </div>
            <div className="col">
              <label className="form-label" htmlFor="budgetMax">&nbsp;</label>
              <div className="input-group">
                <span className="input-group-text">Max</span>
                <input
                  type="number"
                  name="budgetMax"
                  id="budgetMax"
                  className="form-control"
                  placeholder="e.g. 2000000"
                  onChange={handleChange}
                  min="0"
                />
              </div>
            </div>
          </div>


          <div className="d-flex justify-content-end">
            <Button type="submit">Submit</Button>
          </div>
        </form>
      </div>
    </>

  );
};

export default InputBasic;

