import React, { useState } from "react";
import {
    Box,
    Button,
    Card,
    CardContent,
    Typography,
    FormControl,
    FormLabel,
    FormGroup,
    FormControlLabel,
    Checkbox,
    TextField,
    MenuItem,
} from "@mui/material";

const initialFormData = {
    profession: "",
    experienceLevel: "",
    computerUsage: "",

    primaryUses: [],
    specificApps: "",
    multitasking: "",
    useVMs: "",
    industrySoftware: "",

    deviceType: "",
    processorBrand: "",
    needDedicatedGPU: "",
    minRAM: "",
    storagePreference: "",
    batteryImportance: "",
    portsNeeded: "",

    travelFrequency: "",
    environmentCondition: "",

    budgetRange: "",
    newOrUsed: "",
    preferredVendors: "",
    smartSuggestions: "",
    showTransparency: "",
};

const options = {
    experienceLevels: ["Beginner", "Intermediate", "Expert"],
    computerUsageFreq: ["Occasionally", "Daily", "All-day use"],
    primaryUses: [
        "Web Browsing",
        "Office Work",
        "Gaming",
        "Programming",
        "Graphic Design",
        "Video Editing",
    ],
    yesNo: ["Yes", "No"],
    deviceTypes: ["Laptop", "Desktop"],
    processorBrands: ["Intel", "AMD", "No preference"],
    batteryImportance: ["Not important", "Somewhat important", "Very important"],
    travelFrequency: ["Never", "Occasionally", "Frequently"],
    environmentConditions: ["Normal", "Hot", "Dusty"],
    newOrUsedOptions: ["New", "Used"],
    smartSuggestionsOptions: ["Automatic", "Manual"],
    transparencyOptions: ["Yes", "No"],
};

function UserQuestionnaire() {
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState(initialFormData);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        if (type === "checkbox" && name === "primaryUses") {
            const updated = checked
                ? [...formData.primaryUses, value]
                : formData.primaryUses.filter((item) => item !== value);
            setFormData({ ...formData, primaryUses: updated });
        } else {
            setFormData({ ...formData, [name]: value });
        }
    };

    const nextStep = () => step < 5 && setStep(step + 1);
    const prevStep = () => step > 1 && setStep(step - 1);

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log("User Answers:", formData);
        alert("Thank you! Answers saved (check console).");
    };

    const renderSelect = (label, name, choices, required = true) => (
        <TextField
            select
            fullWidth
            margin="normal"
            label={label}
            name={name}
            value={formData[name]}
            onChange={handleChange}
            required={required}
        >
            <MenuItem value="">Select</MenuItem>
            {choices.map((opt) => (
                <MenuItem key={opt} value={opt}>
                    {opt}
                </MenuItem>
            ))}
        </TextField>
    );

    return (
        <Box maxWidth={700} mx="auto" mt={5}>
            <Card elevation={6} sx={{ p: 3 }}>
                <CardContent>
                    <Typography variant="h5" gutterBottom>
                        User Questionnaire (Step {step} of 5)
                    </Typography>
                    <form onSubmit={handleSubmit}>
                        {step === 1 && (
                            <>
                                <TextField
                                    fullWidth
                                    label="Profession or field of work/study"
                                    name="profession"
                                    value={formData.profession}
                                    onChange={handleChange}
                                    required
                                    margin="normal"
                                />
                                {renderSelect("Technical experience level", "experienceLevel", options.experienceLevels)}
                                {renderSelect("How frequently do you use a computer?", "computerUsage", options.computerUsageFreq)}
                            </>
                        )}

                        {step === 2 && (
                            <>
                                <FormControl component="fieldset" sx={{ my: 2 }}>
                                    <FormLabel component="legend">
                                        What do you primarily use a computer for? *
                                    </FormLabel>
                                    <FormGroup row>
                                        {options.primaryUses.map((use) => (
                                            <FormControlLabel
                                                key={use}
                                                control={
                                                    <Checkbox
                                                        checked={formData.primaryUses.includes(use)}
                                                        onChange={handleChange}
                                                        name="primaryUses"
                                                        value={use}
                                                    />
                                                }
                                                label={use}
                                            />
                                        ))}
                                    </FormGroup>
                                </FormControl>
                                <TextField
                                    fullWidth
                                    label="Specific applications/software you use"
                                    name="specificApps"
                                    value={formData.specificApps}
                                    onChange={handleChange}
                                    margin="normal"
                                    placeholder="e.g., Photoshop, VSCode"
                                />
                                {renderSelect("Will you be multitasking?", "multitasking", options.yesNo)}
                                {renderSelect("Do you plan to use virtual machines or emulators?", "useVMs", options.yesNo)}
                                <TextField
                                    fullWidth
                                    label="Industry-specific software (if any)"
                                    name="industrySoftware"
                                    value={formData.industrySoftware}
                                    onChange={handleChange}
                                    margin="normal"
                                    placeholder="e.g., AutoCAD, MATLAB"
                                />
                            </>
                        )}

                        {step === 3 && (
                            <>
                                {renderSelect("Laptop or Desktop?", "deviceType", options.deviceTypes)}
                                {renderSelect("Preferred processor brand", "processorBrand", options.processorBrands)}
                                {renderSelect("Need a dedicated GPU?", "needDedicatedGPU", options.yesNo)}
                                <TextField
                                    fullWidth
                                    label="Minimum RAM (GB)"
                                    name="minRAM"
                                    type="number"
                                    value={formData.minRAM}
                                    onChange={handleChange}
                                    margin="normal"
                                />
                                <TextField
                                    fullWidth
                                    label="Preferred storage type/size"
                                    name="storagePreference"
                                    value={formData.storagePreference}
                                    onChange={handleChange}
                                    margin="normal"
                                />
                                {renderSelect("Battery life importance", "batteryImportance", options.batteryImportance)}
                                <TextField
                                    fullWidth
                                    label="Ports needed (e.g., USB-C, HDMI)"
                                    name="portsNeeded"
                                    value={formData.portsNeeded}
                                    onChange={handleChange}
                                    margin="normal"
                                />
                            </>
                        )}

                        {step === 4 && (
                            <>
                                {renderSelect("Travel frequency", "travelFrequency", options.travelFrequency)}
                                {renderSelect("Work environment", "environmentCondition", options.environmentConditions)}
                            </>
                        )}

                        {step === 5 && (
                            <>
                                <TextField
                                    fullWidth
                                    label="Budget range"
                                    name="budgetRange"
                                    value={formData.budgetRange}
                                    onChange={handleChange}
                                    placeholder="e.g., $500 - $1500"
                                    margin="normal"
                                    required
                                />
                                {renderSelect("New or used?", "newOrUsed", options.newOrUsedOptions)}
                                <TextField
                                    fullWidth
                                    label="Preferred vendors/brands (optional)"
                                    name="preferredVendors"
                                    value={formData.preferredVendors}
                                    onChange={handleChange}
                                    margin="normal"
                                />
                                {renderSelect("Smart suggestions or manual?", "smartSuggestions", options.smartSuggestionsOptions)}
                                {renderSelect("Show transparency of choices?", "showTransparency", options.transparencyOptions)}
                            </>
                        )}

                        <Box mt={3} display="flex" justifyContent="space-between">
                            {step > 1 && (
                                <Button variant="outlined" onClick={prevStep}>
                                    Back
                                </Button>
                            )}
                            {step < 5 ? (
                                <Button variant="contained" onClick={nextStep}>
                                    Next
                                </Button>
                            ) : (
                                <Button variant="contained" type="submit">
                                    Submit
                                </Button>
                            )}
                        </Box>
                    </form>
                </CardContent>
            </Card>
        </Box>
    );
}

export default UserQuestionnaire;
