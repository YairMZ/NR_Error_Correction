function format_figure(fig_handle, varargin)%x_label_str, y_label_str, font_name, font size)
%FORMAT_FIGURE Summary of this function goes here
%   Detailed explanation goes here
ax = fig_handle.CurrentAxes;

%defaults
set(findall(fig_handle,'-property','FontName'),'FontName','mwa_cmr10');
set(findall(fig_handle,'-property','FontSize'),'FontSize',16);
box(ax, 'on');
grid(ax, 'on');

%other stuff and defualt override
for argidx = 1:2:(nargin - 1)
    switch varargin{argidx}
        case 'XLabel'
            xlabel(ax,varargin{argidx+1},'Interpreter','latex');
        case 'YLabel'
            ylabel(ax,varargin{argidx+1},'Interpreter','latex');
        case 'FontName'
            set(findall(fig_handle,'-property','FontName'),'FontName',varargin{argidx+1});
        case 'FontSize'
            set(findall(fig_handle,'-property','FontSize'),'FontSize',varargin{argidx+1});
        case 'box'
            box(ax, varargin{argidx+1});
        case 'grid'
            grid(ax, varargin{argidx+1});
        case 'title'
            title(ax, varargin{argidx+1})
        otherwise
            set(findall(fig_handle,'-property',varargin{argidx}),varargin{argidx},varargin{argidx+1})
    end
end
end