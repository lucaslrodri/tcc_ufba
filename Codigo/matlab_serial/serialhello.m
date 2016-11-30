function serialhello
    porta_com = 'COM13';
    porta_com2 = 'COM3';
    current_buffer1 = get_data(porta_com);
    
    current_buffer2 = get_data(porta_com2);
    figure;
    hold all;
    t1 = linspace(0,500,length(current_buffer1));
    t2 = linspace(0,500,length(current_buffer2));
    p1 = plot(t1,current_buffer1);
    p2 = plot(t2,current_buffer2,'--');
    hold off;
    xlabel('Tempo (us)');
    ylabel('Amplitude(bits)');
    ylim([0,4095]);
    xlim([0,100]);
    while true
        current_buffer1 = get_data(porta_com);
        t1 = linspace(0,500,length(current_buffer1));
        pause(0.001);
        set(p1,'YData',current_buffer1);
        set(p1,'XData',t1);
        current_buffer2 = get_data(porta_com2);
        pause(0.001);
        t2 = linspace(0,500,length(current_buffer2));
        pause(0.001);
        set(p2,'YData',current_buffer2);
        set(p2,'XData',t2);
        pause(0.001);
        drawnow;
    end
end

function buffer = get_data(porta_com)
    s = serial(porta_com);
    set(s,'BaudRate',921600);
    fopen(s);
    temp_str = fscanf(s);
    temp_str = strsplit(temp_str);
    buffer = zeros(1,length(temp_str));
    for i = 1:length(temp_str)
        [temp_val, status] = str2num(temp_str{i});
        if status == true
            buffer(i) = temp_val;
        else
            buffer(i) = NaN;
        end
    end
    fclose(s);
    pause(0.1);
end