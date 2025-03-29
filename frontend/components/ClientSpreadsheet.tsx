"use client";

import React from "react";
import {
  SpreadsheetComponent,
  SheetsDirective,
  SheetDirective,
} from "@syncfusion/ej2-react-spreadsheet";
import "@syncfusion/ej2-base/styles/material.css";
import "@syncfusion/ej2-buttons/styles/material.css";
import "@syncfusion/ej2-inputs/styles/material.css";
import "@syncfusion/ej2-popups/styles/material.css";
import "@syncfusion/ej2-react-spreadsheet/styles/material.css";

import { registerLicense } from "@syncfusion/ej2-base";

registerLicense(process.env.NEXT_PUBLIC_SYNCFUSION_LICENSE!);

const ClientSpreadsheet = () => {
  return (
    <>
      <SpreadsheetComponent
        allowOpen={true} // Enable file opening
        allowSave={true} // Enable file saving
        saveUrl="https://services.syncfusion.com/react/production/api/spreadsheet/save"
        openUrl="https://services.syncfusion.com/react/production/api/spreadsheet/open"
        height="100vh"
      >
        {/* <SheetsDirective>
        <SheetDirective>

        </SheetDirective>
      </SheetsDirective> */}
      </SpreadsheetComponent>
    </>
  );
};

export default ClientSpreadsheet;
